# BetterVencordPatch
An efficient program which lets you install Vencord without user interaction and (optionally) patches Vencord whenever Discord updates.</br>
Vencord doesn't automatically patch itself when Discord updates, so BetterVencordPatch offers a fix for that.

## Features
- BetterVencordPatch can patch Vencord without any user interaction, unlike the official installer
    - This is due to modifications made to the installer source. All references to UI in cli.go have been removed for optimization purposes.
    - **You can disable the auto-patch functionality in the installer while still being able to install Vencord without a UI.**
- Patch Vencord (and optionally OpenAsar) automatically, even through Discord updates
- Notifications are used to communicate success, failure, and errors

# Installing BetterVencordPatch
Download and run INSTALLER.exe or INSTALLER from the latest release, depending on your OS.</br>
On macOS, you must run `chmod +x` to make the installer executable.</br>
All the required files will be downloaded for you.

## Installing from Source
**You have much more control over your installation when installing from source, including the Discord branch which is patched and whether or not to send notifications on success.**</br>
All original requirements for building the official installer apply here.</br>
Run install_[YOUR OPERATING SYSTEM].py to install BetterVencordPatch from source.</br>
To install from source, install Python 3.x and Go 1.25.x. The dependencies will automatically be installed.

# Building from Source
If you want build BetterVencordPatch and/or its autopatcher without installing BetterVencordPatch, see below.</br>
To build from source, install Python 3.x and Go 1.25.x.
Make sure not to put quotes around any arguments.

## Building the Installer
You can use these commands to build the installer (arguments explained below):
- Windows: `go build -ldflags="-H=windowsgui -X main.branch=BRANCH -X main.patchOpenAsar=USE_OPEN_ASAR -X main.sendSuccessNotifications=SEND_SUCCESS_NOTIFICATIONS" --tags cli`
- macOS: `go build -ldflags="-X main.branch=BRANCH -X main.patchOpenAsar=USE_OPEN_ASAR -X main.sendSuccessNotifications=SEND_SUCCESS_NOTIFICATIONS" --tags cli`
- Windows (simplified): `go build -ldflags="-H=windowsgui" --tags cli`
- macOS (simplified): `go build --tags cli`

These arguments can be used to customize the Vencord installer:
- BRANCH: The Discord branch that BetterVencordPatch will patch
    - Type: string
    - Possible values: stable | ptb | canary
- USE_OPEN_ASAR: If the installer will patch OpenAsar
    - Type: boolean
    - Possible values: true | false
- SEND_SUCCESS_NOTIFICATIONS: If the installer will send a success notification on success
    - Type: boolean
    - Possible values: true | false

By default, vencordinstaller.exe should be in C:\Users\USER\AppData\Local\introvertednoob\BetterVencordPatch\ (Windows only).

## Building the Auto-patcher
You can use these commands to build the auto-patcher (arguments explained below):
- Windows: `go build -ldflags="-H=windowsgui -X main.branch=BRANCH" --tags avp_win -o autovencordpatch.exe`
- macOS: `go build -ldflags="-X main.branch=BRANCH" --tags avp_macos -o autovencordpatch`

These arguments can be used to customize the auto-patcher:
- BRANCH: The branch of Discord that will be watched for updates
    - Type: string
    - Possible values: stable | ptb | canary

By default, autovencordpatch.exe should be in C:\Users\USER\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\ (Windows only).

## Credits
Auto-patcher created by [Aaron Wijesinghe](https://github.com/AaronWijesinghe)

This software uses a modified version of the [Vencord Installer](https://github.com/Vencord/Installer)</br>
Copyright (c) 2023 Vendicated and Vencord contributors</br>
Licensed under the GNU General Public License v3.0</br>
