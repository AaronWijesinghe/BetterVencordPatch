//go:build avp_win

package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"syscall"
	"time"

	"github.com/fsnotify/fsnotify"
	"golang.org/x/sys/windows"
)

const (
	checkInterval = 1 * time.Second
)

var suffixes = map[string]string{
	"stable": "",
	"ptb":    "PTB",
	"canary": "Canary",
}
var branch = "stable"
var foundUpdate bool

func getDirSize(path string) (int64, error) {
	var size int64

	err := filepath.Walk(path, func(_ string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if !info.IsDir() {
			size += info.Size()
		}
		return nil
	})

	return size, err
}

func waitForUpdateToFinish(dir string) {
	const (
		checkInterval = 500 * time.Millisecond
		stableTime    = 2 * time.Second
	)

	var lastSize int64
	var stableSince time.Time

	for {
		size, err := getDirSize(dir)
		if err != nil {
			fmt.Println("["+time.Now().Format("2006-01-02 15:04:05")+"] Error checking directory size:", err)
			time.Sleep(checkInterval)
			continue
		}

		fmt.Printf("["+time.Now().Format("2006-01-02 15:04:05")+"] New app directory size: %.2f MB\n", float64(size)/(1024*1024))

		if size != lastSize {
			lastSize = size
			stableSince = time.Now()
		}

		if !stableSince.IsZero() && time.Since(stableSince) >= stableTime {
			return
		}

		time.Sleep(checkInterval)
	}
}

func runInstaller() {
	cmd := exec.Command(filepath.Join(os.Getenv("LOCALAPPDATA"), "bettervencordpatch/vencordinstaller.exe"))
	cmd.SysProcAttr = &syscall.SysProcAttr{
		HideWindow:    true,
		CreationFlags: windows.CREATE_NO_WINDOW,
	}
	err := cmd.Run()
	if err != nil {
		fmt.Println("["+time.Now().Format("2006-01-02 15:04:05")+"] Failed to run installer:", err)
	}
}

func killDiscord() {
	cmd := exec.Command("C:\\Windows\\System32\\taskkill.exe", "/f", "/im", "bettervencordpatch/vencordinstaller.exe")
	cmd.SysProcAttr = &syscall.SysProcAttr{
		HideWindow:    true,
		CreationFlags: windows.CREATE_NO_WINDOW,
	}
	err := cmd.Start()
	if err != nil {
		fmt.Println("["+time.Now().Format("2006-01-02 15:04:05")+"] Failed to kill Discord:", err)
	}
}

func startDiscord() {
	cmd := exec.Command(filepath.Join(os.Getenv("LOCALAPPDATA"), "Discord"+suffixes[branch]+"/Update.exe"), "--processStart", "Discord.exe")
	cmd.SysProcAttr = &syscall.SysProcAttr{
		HideWindow:    true,
		CreationFlags: windows.CREATE_NO_WINDOW,
	}
	err := cmd.Start()
	if err != nil {
		fmt.Println("["+time.Now().Format("2006-01-02 15:04:05")+"] Failed to start Discord:", err)
	}
}

func watchDiscord(discordDir string) {
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		fmt.Println("["+time.Now().Format("2006-01-02 15:04:05")+"] Failed to create watcher:", err)
		return
	}
	defer watcher.Close()

	err = watcher.Add(discordDir)
	if err != nil {
		fmt.Println("["+time.Now().Format("2006-01-02 15:04:05")+"] Failed to add watcher:", err)
		return
	}

	fmt.Println("[" + time.Now().Format("2006-01-02 15:04:05") + "] Watching for Discord updates...")

	for {
		select {
		case event := <-watcher.Events:
			if !foundUpdate && strings.Contains(filepath.Clean(event.Name), "app-") && event.Op&fsnotify.Create == fsnotify.Create {
				fmt.Println("[" + time.Now().Format("2006-01-02 15:04:05") + "] App update detected...")
				fmt.Println(filepath.Clean(event.Name))
				watcher.Add(filepath.Clean(event.Name))
				foundUpdate = true
				waitForUpdateToFinish(filepath.Clean(event.Name))
			}
			if foundUpdate {
				fmt.Println("[" + time.Now().Format("2006-01-02 15:04:05") + "] Discord has finished updating, patching Vencord...")
				killDiscord()
				time.Sleep(time.Second * 1)
				runInstaller()
				startDiscord()
				fmt.Println("[" + time.Now().Format("2006-01-02 15:04:05") + "] Attempted to patch Vencord.")
				foundUpdate = false
				return
			}
		case err := <-watcher.Errors:
			fmt.Println("Watcher error:", err)
			time.Sleep(checkInterval)
		}
	}
}

func main() {
	discordPath := filepath.Clean(filepath.Join(os.Getenv("LOCALAPPDATA"), "Discord"+suffixes[branch]))
	fmt.Println(discordPath)

	for {
		watchDiscord(discordPath)
	}
}
