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

func main() {
	var lastUpdate time.Time

	discordPath := filepath.Clean(filepath.Join(os.Getenv("LOCALAPPDATA"), "Discord"+suffixes[branch]))
	fmt.Println(discordPath)
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		fmt.Println("["+time.Now().Format("2006-01-02 15:04:05")+"] Failed to create watcher:", err)
		return
	}
	defer watcher.Close()

	err = watcher.Add(discordPath)
	if err != nil {
		fmt.Println("["+time.Now().Format("2006-01-02 15:04:05")+"] Failed to add watcher:", err)
		return
	}

	fmt.Println("[" + time.Now().Format("2006-01-02 15:04:05") + "] Watching for Discord updates...")

	for {
		select {
		case event := <-watcher.Events:
			if strings.Contains(filepath.Clean(event.Name), "app-") {
				if event.Op&fsnotify.Create == fsnotify.Create {
					if time.Since(lastUpdate) > 30*time.Second {
						lastUpdate = time.Now()
						fmt.Println("[" + time.Now().Format("2006-01-02 15:04:05") + "] App update detected, patching Vencord in 5s...")
						time.Sleep(time.Second * 5)
						fmt.Println("[" + time.Now().Format("2006-01-02 15:04:05") + "] Discord has finished updating, re-opening Discord...")
						killDiscord()
						time.Sleep(time.Second * 2)
						runInstaller()
						startDiscord()
					}
				}
			}
		case err := <-watcher.Errors:
			fmt.Println("Watcher error:", err)
			time.Sleep(checkInterval)
		}
	}
}
