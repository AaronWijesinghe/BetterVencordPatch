//go:build cli

/*
 * SPDX-License-Identifier: GPL-3.0
 * Vencord Installer, a cross platform gui/cli app for installing Vencord
 * Copyright (c) 2023 Vendicated and Vencord contributors
 */

package main

import (
	"bytes"
	"errors"
	"io"
	"net/http"
	"os"
	path "path/filepath"
	"strconv"
)

// Fetched via the GitHub API (rather than the raw download URL) so we also receive the
// published SHA-256 digest used to verify the asar before installing it.
const OpenAsarReleaseUrl = "https://api.github.com/repos/GooseMod/OpenAsar/releases/tags/nightly"

func FindAsarFile(dir string) (*os.File, error) {
	for _, file := range []string{"_app.asar", "app.asar"} {
		f, err := os.Open(path.Join(dir, file))
		if err != nil {
			continue
		}
		stats, err := f.Stat()
		if err == nil && !stats.IsDir() {
			return f, nil
		}
		_ = f.Close()
	}
	return nil, errors.New("The install at " + dir + " has no asar file")
}

func (di *DiscordInstall) IsOpenAsar() (retBool bool) {
	if di.isOpenAsar != nil {
		return *di.isOpenAsar
	}

	defer func() {
		Log.Debug("Checking if", di.path, "is using OpenAsar:", retBool)
		di.isOpenAsar = &retBool
	}()

	asarFile, err := FindAsarFile(path.Join(di.appPath, ".."))
	if err != nil {
		Log.Error(err.Error())
		return false
	}

	b, err := io.ReadAll(asarFile)
	_ = asarFile.Close()
	if err != nil {
		Log.Error(err.Error())
		return false
	}

	if bytes.Contains(b, []byte("OpenAsar")) {
		return true
	}

	return false
}

func (di *DiscordInstall) InstallOpenAsar() error {
	PreparePatch(di)

	dir := path.Join(di.appPath, "..")
	asarFile, err := FindAsarFile(dir)
	if err != nil {
		return err
	}
	_ = asarFile.Close()

	if err = os.Rename(asarFile.Name(), path.Join(dir, "app.asar.backup")); err != nil {
		if errors.Is(err, os.ErrPermission) {
			return errors.New("The App Management/Full Disk Access permission must be granted to allow VencordInstaller to patch OpenAsar. Make sure Discord isn't running!")
		}
		return err
	}

	release, err := GetGithubRelease(OpenAsarReleaseUrl, OpenAsarReleaseUrl)
	if err != nil {
		return err
	}

	var downloadUrl, digest string
	for _, asset := range release.Assets {
		if asset.Name == "app.asar" {
			downloadUrl = asset.DownloadURL
			digest = asset.Digest
			break
		}
	}
	if downloadUrl == "" {
		return errors.New("Could not find app.asar in the latest OpenAsar release")
	}

	res, err := http.Get(downloadUrl)
	if err != nil {
		return err
	} else if res.StatusCode >= 300 {
		return errors.New("Failed to fetch OpenAsar - " + strconv.Itoa(res.StatusCode) + ": " + res.Status)
	}
	defer res.Body.Close()

	data, err := io.ReadAll(res.Body)
	if err != nil {
		return err
	}

	// Verify against the SHA-256 GitHub published before writing the asar Discord will run.
	if err = verifyDigest("app.asar", data, digest); err != nil {
		return err
	}

	if err = os.WriteFile(asarFile.Name(), data, 0644); err != nil {
		return err
	}

	di.isOpenAsar = Ptr(true)
	return nil
}

func (di *DiscordInstall) UninstallOpenAsar() error {
	PreparePatch(di)

	dir := path.Join(di.appPath, "..")
	// .original is our old name
	// OpenAsar's updater uses .backup, so we now also use that - .original is deprecated
	for _, file := range []string{path.Join(dir, "app.asar.backup"), path.Join(dir, "app.asar.original")} {
		if !ExistsFile(file) {
			continue
		}

		asarFile, err := FindAsarFile(dir)
		if err != nil {
			return err
		}
		_ = asarFile.Close()

		if err = os.Rename(file, asarFile.Name()); err != nil {
			return err
		}

		di.isOpenAsar = Ptr(false)
		return nil
	}

	return errors.New("No app.asar.backup. Reinstall Discord.")
}
