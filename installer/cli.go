//go:build cli

/*
 * SPDX-License-Identifier: GPL-3.0
 * Vencord Installer, a cross platform gui/cli app for installing Vencord
 * Copyright (c) 2023 Vendicated and Vencord contributors
 */

package main

import (
	"flag"
	"fmt"
	"os"
	"runtime"

	"github.com/fatih/color"
)

var discords []any

func isValidBranch(branch string) bool {
	switch branch {
	case "", "stable", "ptb", "canary", "auto":
		return true
	default:
		return false
	}
}

func die(msg string) {
	Log.Error(msg)
	exitFailure(msg)
}

var pyBranch = "stable"
var pyOpenAsar = false
var pySendSuccessNotifications = true

func main() {
	InitGithubDownloader()
	discords = FindDiscords()

	// Used by log.go init func
	flag.Bool("debug", false, "Enable debug info")

	var versionFlag = flag.Bool("version", false, "View the program version")
	var installFlag = flag.Bool("install", !pyOpenAsar, "Install Vencord")
	var updateFlag = flag.Bool("repair", false, "Repair Vencord")
	var uninstallFlag = flag.Bool("uninstall", false, "Uninstall Vencord")
	var installOpenAsarFlag = flag.Bool("install-openasar", pyOpenAsar, "Install OpenAsar")
	var uninstallOpenAsarFlag = flag.Bool("uninstall-openasar", false, "Uninstall OpenAsar")
	var locationFlag = flag.String("location", "", "The location of the Discord install to modify")
	var branchFlag = flag.String("branch", pyBranch, "The branch of Discord to modify [auto|stable|ptb|canary]")
	flag.Parse()

	if *versionFlag {
		fmt.Println("Vencord Installer CLI v1.4.0 (modified)")
		fmt.Println("Modified by @introvertednoob to install Vencord without user interaction")
		fmt.Println("\nCopyright (C) 2023 Vendicated and Vencord contributors")
		fmt.Println("License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.")
		return
	}

	if *locationFlag != "" && *branchFlag != "" {
		die("The 'location' and 'branch' flags are mutually exclusive.")
	}

	if !isValidBranch(*branchFlag) {
		die("The 'branch' flag must be one of the following: [auto|stable|ptb|canary]")
	}

	if *installFlag || *updateFlag {
		if !<-GithubDoneChan {
			die("Not " + Ternary(*installFlag, "installing", "updating") + " as fetching release data failed.")
		}
	}

	install, uninstall, update, installOpenAsar, uninstallOpenAsar := *installFlag, *uninstallFlag, *updateFlag, *installOpenAsarFlag, *uninstallOpenAsarFlag

	var err error
	var errSilent error
	if install {
		errSilent = PromptDiscord("patch", *locationFlag, *branchFlag).patch()
	} else if uninstall {
		errSilent = PromptDiscord("unpatch", *locationFlag, *branchFlag).unpatch()
	} else if update {
		Log.Info("Downloading latest Vencord files...")
		err := installLatestBuilds()
		Log.Info("Done!")
		if err == nil {
			errSilent = PromptDiscord("repair", *locationFlag, *branchFlag).patch()
		}
	} else if uninstallOpenAsar {
		discord := PromptDiscord("patch", *locationFlag, *branchFlag)
		if discord.IsOpenAsar() {
			err = discord.UninstallOpenAsar()
		} else {
			die("OpenAsar is not installed.")
		}
	} else if installOpenAsar {
		discord := PromptDiscord("patch", *locationFlag, *branchFlag)
		if !discord.IsOpenAsar() {
			err = discord.InstallOpenAsar()
		} else {
			die("OpenAsar is already installed.")
		}
	}

	if err != nil {
		Log.Error(err)
		exitFailure()
	}
	if errSilent != nil {
		exitFailure()
	}

	exitSuccess()
}

func exitSuccess() {
	if pySendSuccessNotifications == true {
		if runtime.GOOS == "darwin" {
			notify("BetterVencordPatch", "Successfully installed Vencord!")
		} else {
			notify("Success", "Successfully installed Vencord!")
		}
	}
	color.HiGreen("✔ Success!")
	os.Exit(0)
}

func exitFailure(reason ...string) {
	displayed_reason := "Failed to patch Vencord"
	if len(reason) > 0 {
		displayed_reason = "Failed to patch Vencord: " + reason[0]
	}
	color.HiRed("❌ Failed!")
	//cmd := exec.Command("osascript", "-e", `display notification "`++`" with title "VencordInstaller"`)

	if runtime.GOOS == "darwin" {
		notify("BetterVencordPatch", displayed_reason)
	} else {
		notify("An error has occured.", displayed_reason)
	}
	os.Exit(1)
}

func PromptDiscord(action, dir, branch string) *DiscordInstall {
	for _, discord := range discords {
		install := discord.(*DiscordInstall)
		if install.branch == branch {
			return install
		}
	}
	die("No Discord install was found. Try manually specifying it with the --dir flag.")
	return nil
}

func InstallLatestBuilds() error {
	return installLatestBuilds()
}

func HandleScuffedInstall() {
	fmt.Println("Hold on!")
	fmt.Println("You have a broken Discord install.")
	fmt.Println("Please reinstall Discord before proceeding!")
	fmt.Println("Otherwise, Vencord will likely not work.")
}
