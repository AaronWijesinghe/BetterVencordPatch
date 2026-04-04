//go:build avp_win

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

var discordBranchSuffix = ""

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
	cmd := exec.Command(filepath.Join(os.Getenv("LOCALAPPDATA"), "Discord"+discordBranchSuffix+"/Update.exe"), "--processStart", "Discord.exe")
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

	discordJSON := filepath.Clean(filepath.Join(os.Getenv("LOCALAPPDATA"), "Discord"+discordBranchSuffix+"/app.ico"))
	fmt.Println(discordJSON)
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

	for {
		select {
		case event := <-watcher.Events:
			if filepath.Clean(event.Name) == discordJSON {
				if event.Op&fsnotify.Create == fsnotify.Create || event.Op&fsnotify.Write == fsnotify.Write || event.Op&fsnotify.Remove == fsnotify.Remove {
					if time.Since(lastUpdate) > 30*time.Second {
						lastUpdate = time.Now()
						fmt.Println("[" + time.Now().Format("2006-01-02 15:04:05") + "] Icon update detected, patching Vencord in 10s...")
						time.Sleep(time.Second * 10)
						fmt.Println("[" + time.Now().Format("2006-01-02 15:04:05") + "] Discord has (likely) finished updating, re-opening Discord...")
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
