# BetterVencordPatch (macOS)
An efficient program which lets you install Vencord without user interaction and (optionally) patches Vencord whenever Discord updates on macOS.</br>
On macOS, Vencord doesn't automatically patch itself when Discord updates, so BetterVencordPatch offers a fix for that.

## Features
- VencordInstaller.app can patch Vencord without any user interaction, unlike the official installer
    - This is due to modifications made to the installer source. All references to UI in cli.go have been removed for optimization purposes.
    - **You can disable the auto-patch functionality in the installer while still being able to install Vencord without a UI.**
- Patch Vencord (and optionally OpenAsar) automatically, even through Discord updates
- Notifications are used to communicate success, failure, and errors

## Requirements
All original requirements for building the official installer apply here.</br>
Go 1.25.x is also recommended, but you can probably use a lower version instead.</br>
**NOTE: The only supported OS for this project is macOS (for now).**

## Installation
Run install.py to install BetterVencordPatch.</br>
~~I may release a pre-built app with the launchd plist through GitHub Releases soon™.~~

## Credits
Auto-patcher created by [Aaron Wijesinghe](https://github.com/introvertednoob)

This software uses a modified version of the [Vencord Installer](https://github.com/Vencord/Installer)</br>
Copyright (c) 2023 Vendicated and Vencord contributors</br>
Licensed under the GNU General Public License v3.0</br>
