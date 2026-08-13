//go:build windows
// +build windows

package main

import (
	"github.com/gen2brain/beeep"
)

func notify(title, message string) error {
	// notification := toast.Notification{
	// 	AppID:   "BetterVencordPatch",
	// 	Title:   title,
	// 	Message: message,
	// }
	// return notification.Push()
	err := beeep.Notify(title, message, "")
	return err
}
