package main

import (
	"fmt"
	"os/exec"
	"path/filepath"
	"time"

	"github.com/fsnotify/fsnotify"
)

const (
	discordJSON   = "/Applications/Discord.app/Contents/Resources/build_info.json"
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
			if filepath.Clean(event.Name) == discordJSON && event.Op&fsnotify.Create == fsnotify.Create {
				fmt.Println("[" + time.Now().Format("2006-01-02 15:04:05") + "] Discord is updating, running Vencord installer...")
				time.Sleep(1.0 * time.Second)
				runInstaller()
			}
		case err := <-watcher.Errors:
			fmt.Println("Watcher error:", err)
			time.Sleep(checkInterval)
		}
	}
}
