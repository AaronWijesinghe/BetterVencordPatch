//go:build darwin
// +build darwin

package main

import (
	"os/exec"
)

func notify(title, message string) error {
	// Uses AppleScript for macOS notifications
	return exec.Command("osascript", "-e",
		`display notification "`+message+`" with title "`+title+`"`).Run()
}
