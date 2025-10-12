package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"syscall"
	"time"

	"github.com/fsnotify/fsnotify"
	"golang.org/x/sys/windows"
)

const (
	checkInterval = 1 * time.Second
)

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
		fmt.Println("["+time.Now().Format("2006-01-02 15:04:05")+"] Failed to run installer:", err)
	}
}

func startDiscord() {
	cmd := exec.Command(filepath.Join(os.Getenv("LOCALAPPDATA"), "Discord/Update.exe"), "--processStart", "Discord.exe")
	cmd.SysProcAttr = &syscall.SysProcAttr{
		HideWindow:    true,
		CreationFlags: windows.CREATE_NO_WINDOW,
	}
	err := cmd.Start()
	if err != nil {
		fmt.Println("["+time.Now().Format("2006-01-02 15:04:05")+"] Failed to run installer:", err)
	}
}

func main() {
	discordJSON := filepath.Join(os.Getenv("LOCALAPPDATA"), "Discord/rm-1")
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		fmt.Println("["+time.Now().Format("2006-01-02 15:04:05")+"] Failed to create watcher:", err)
		return
	}
	defer watcher.Close()

	dir := filepath.Dir(discordJSON)
	err = watcher.Add(dir)
	if err != nil {
		fmt.Println("["+time.Now().Format("2006-01-02 15:04:05")+"] Failed to add watcher:", err)
		return
	}

	fmt.Println("[" + time.Now().Format("2006-01-02 15:04:05") + "] Watching for Discord updates...")

	rms := 0
	for {
		select {
		case event := <-watcher.Events:
			if filepath.Clean(event.Name) == discordJSON && event.Op&fsnotify.Remove == fsnotify.Remove && rms == 1 {
				fmt.Println("[" + time.Now().Format("2006-01-02 15:04:05") + "] Discord has finished updating, re-opening Discord...")
				killDiscord()
				runInstaller()
				startDiscord()
				rms = 0
			} else if filepath.Clean(event.Name) == discordJSON && event.Op&fsnotify.Remove == fsnotify.Remove {
				rms = 1
			}
		case err := <-watcher.Errors:
			fmt.Println("Watcher error:", err)
			time.Sleep(checkInterval)
		}
	}
}
