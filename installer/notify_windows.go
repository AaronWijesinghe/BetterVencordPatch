//go:build windows
// +build windows

package main

import (
	"github.com/go-toast/toast"
)

func notify(title, message string) error {
	notification := toast.Notification{
		AppID:   "BetterVencordPatch",
		Title:   title,
		Message: message,
	}
	return notification.Push()
}
