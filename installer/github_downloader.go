//go:build cli

/*
 * SPDX-License-Identifier: GPL-3.0
 * Vencord Installer, a cross platform gui/cli app for installing Vencord
 * Copyright (c) 2023 Vendicated and Vencord contributors
 */

package main

import (
	"bufio"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	path "path/filepath"
	"strconv"
	"strings"
	"sync"
)

// verifyDigest checks that data matches the GitHub-published digest (e.g. "sha256:abc...").
// If digest is empty (e.g. the vencord.dev fallback didn't supply one), verification is
// skipped with a warning rather than failing the install.
func verifyDigest(name string, data []byte, digest string) error {
	if digest == "" {
		Log.Warn("No digest published for", name, "- skipping hash verification")
		return nil
	}

	expected, ok := strings.CutPrefix(digest, "sha256:")
	if !ok {
		return errors.New("Unsupported digest format for " + name + ": " + digest)
	}

	sum := sha256.Sum256(data)
	actual := hex.EncodeToString(sum[:])
	if !strings.EqualFold(actual, expected) {
		return errors.New("Hash mismatch for " + name + " - expected " + expected + " but got " + actual + ". Refusing to install possibly tampered file.")
	}

	Log.Debug("Verified SHA-256 of", name)
	return nil
}

type GithubRelease struct {
	Name    string `json:"name"`
	TagName string `json:"tag_name"`
	Assets  []struct {
		Name        string `json:"name"`
		DownloadURL string `json:"browser_download_url"`
		// Digest is the integrity hash GitHub publishes for each asset, e.g. "sha256:abc...".
		// It is served over the authenticated api.github.com TLS response, so we treat it as
		// the trusted source of truth for verifying the bytes we download.
		Digest string `json:"digest"`
	} `json:"assets"`
}

var ReleaseData GithubRelease
var GithubError error
var GithubDoneChan chan bool

var InstalledHash = "None"
var LatestHash = "Unknown"
var IsDevInstall bool

func GetGithubRelease(url, fallbackUrl string) (*GithubRelease, error) {
	Log.Debug("Fetching", url)

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		Log.Error("Failed to create Request", err)
		return nil, err
	}

	req.Header.Set("User-Agent", UserAgent)

	res, err := http.DefaultClient.Do(req)
	if err != nil {
		Log.Error("Failed to send Request", err)
		return nil, err
	}

	defer res.Body.Close()

	if res.StatusCode >= 300 {
		isRateLimitedOrBlocked := res.StatusCode == 401 || res.StatusCode == 403 || res.StatusCode == 429
		triedFallback := url == fallbackUrl

		// GitHub has a very strict 60 req/h rate limit and some (mostly indian) isps block github for some reason.
		// If that is the case, try our fallback at https://vencord.dev/releases/project
		if isRateLimitedOrBlocked && !triedFallback {
			Log.Error(fmt.Sprintf("Failed to fetch %s (status code %d). Trying fallback URL %s", url, res.StatusCode, fallbackUrl))
			return GetGithubRelease(fallbackUrl, fallbackUrl)
		}

		err = errors.New(res.Status)
		Log.Error(url, "returned Non-OK status", GithubError)
		return nil, err
	}

	var data GithubRelease

	if err = json.NewDecoder(res.Body).Decode(&data); err != nil {
		Log.Error("Failed to decode GitHub JSON Response", err)
		return nil, err
	}

	return &data, nil
}

func InitGithubDownloader() {
	GithubDoneChan = make(chan bool, 1)

	IsDevInstall = os.Getenv("VENCORD_DEV_INSTALL") == "1"
	Log.Debug("Is dev install: ", IsDevInstall)
	if IsDevInstall {
		GithubDoneChan <- true
		return
	}

	go func() {
		// Make sure UI updates once the request either finished or failed
		defer func() {
			GithubDoneChan <- GithubError == nil
		}()

		data, err := GetGithubRelease(ReleaseUrl, ReleaseUrlFallback)
		if err != nil {
			GithubError = err
			return
		}

		ReleaseData = *data

		i := strings.LastIndex(data.Name, " ") + 1
		LatestHash = data.Name[i:]
		Log.Debug("Finished fetching GitHub data")
		Log.Debug("Latest hash is", LatestHash, "Local install is", Ternary(LatestHash == InstalledHash, "up to date!", "outdated!"))
	}()

	// Check hash of installed version if exists
	f, err := os.Open(Patcher)
	if err != nil {
		return
	}
	//goland:noinspection GoUnhandledErrorResult
	defer f.Close()

	Log.Debug("Found existing Vencord install. Checking for hash...")
	scanner := bufio.NewScanner(f)
	if scanner.Scan() {
		line := scanner.Text()
		if strings.HasPrefix(line, "// Vencord ") {
			InstalledHash = line[11:]
			Log.Debug("Existing hash is", InstalledHash)
		} else {
			Log.Debug("Didn't find hash")
		}
	}
}

func installLatestBuilds() (retErr error) {
	Log.Debug("Installing latest builds...")

	// create an empty package.json file in our files dir.
	// without this, node will walk up the file tree and search for a package.json in the
	// parent folders. This might lead to issues if the user for example has ~/package.json
	// with type: "module" in it
	pkgJsonFile := path.Join(FilesDir, "package.json")
	err := os.WriteFile(pkgJsonFile, []byte("{}"), 0644)
	if err != nil {
		Log.Warn("Failed to create", pkgJsonFile, err)
	}

	var wg sync.WaitGroup

	for _, ass := range ReleaseData.Assets {
		if strings.HasPrefix(ass.Name, "patcher.js") ||
			strings.HasPrefix(ass.Name, "preload.js") ||
			strings.HasPrefix(ass.Name, "renderer.js") ||
			strings.HasPrefix(ass.Name, "renderer.css") {
			wg.Add(1)
			ass := ass // Need to do this to not have the variable be overwritten halfway through
			go func() {
				defer wg.Done()
				Log.Debug("Downloading file", ass.Name)

				res, err := http.Get(ass.DownloadURL)
				if err == nil && res.StatusCode >= 300 {
					err = errors.New(res.Status)
				}
				if err != nil {
					Log.Error("Failed to download", ass.Name+":", err)
					retErr = err
					return
				}
				defer res.Body.Close()

				// Buffer the asset so we can verify it in full before writing it to disk.
				// These files are small (a few hundred KB at most).
				data, err := io.ReadAll(res.Body)
				if err != nil {
					Log.Error("Failed to download", ass.Name+":", err)
					retErr = err
					return
				}

				contentLength := res.Header.Get("Content-Length")
				read := strconv.FormatInt(int64(len(data)), 10)
				if contentLength != "" && read != contentLength {
					err = errors.New("Unexpected end of input. Content-Length was " + contentLength + ", but I only read " + read)
					Log.Error(err.Error())
					retErr = err
					return
				}

				// Verify the bytes match the SHA-256 GitHub published for this asset before
				// writing anything that Discord will later execute.
				if err = verifyDigest(ass.Name, data, ass.Digest); err != nil {
					Log.Error(err.Error())
					retErr = err
					return
				}

				outFile := path.Join(FilesDir, ass.Name)
				if err = os.WriteFile(outFile, data, 0644); err != nil {
					Log.Error("Failed to write", outFile+":", err)
					retErr = err
					return
				}
			}()
		}
	}

	wg.Wait()
	Log.Debug("Done!")
	_ = FixOwnership(FilesDir)

	InstalledHash = LatestHash
	return
}
