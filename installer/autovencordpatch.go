//go:build avp_macos

package main

import (
	"fmt"
	"os/exec"
	"path/filepath"
	"time"

	"github.com/fsnotify/fsnotify"
)

var discordAppName = "Discord.app"
var discordJSON = "/Applications/" + discordAppName + "/Contents/Resources/build_info.json"
var discordASAR = "/Applications/" + discordAppName + "/Contents/Resources/app.asar"

const (
	vencordApp    = "/Applications/VencordInstaller.app"
	checkInterval = 1 * time.Second
)

func runInstaller() {
	cmd := exec.Command("open", vencordApp)
	err := cmd.Start()
	if err != nil {
		fmt.Println("["+time.Now().Format("2006-01-02 15:04:05")+"] Failed to run installer:", err)
	}
}

func main() {
	asarUpdated := false
	buildInfoUpdated := false

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
			if filepath.Clean(event.Name) == discordJSON && (event.Op&fsnotify.Create == fsnotify.Create) {
				fmt.Println("[" + time.Now().Format("2006-01-02 15:04:05") + "] Discord build info updated...")
				buildInfoUpdated = true
			}

			if filepath.Clean(event.Name) == discordASAR && (event.Op&fsnotify.Create == fsnotify.Create) {
				fmt.Println("[" + time.Now().Format("2006-01-02 15:04:05") + "] Discord ASAR written...")
				asarUpdated = true
			}

			if asarUpdated && buildInfoUpdated {
				time.Sleep(1.0 * time.Second)
				runInstaller()
				buildInfoUpdated = false
				asarUpdated = false
				fmt.Println("[" + time.Now().Format("2006-01-02 15:04:05") + "] Installer launched, waiting for next update...")
			}
		case err := <-watcher.Errors:
			fmt.Println("Watcher error:", err)
			time.Sleep(checkInterval)
		}
	}
}
