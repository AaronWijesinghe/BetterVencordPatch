# BetterVencordPatch
An efficient program which lets you install Vencord without user interaction and (optionally) patches Vencord whenever Discord updates.</br>
Vencord doesn't automatically patch itself when Discord updates, so BetterVencordPatch offers a fix for that.

## Features
- VencordInstaller.app can patch Vencord without any user interaction, unlike the official installer
    - This is due to modifications made to the installer source. All references to UI in cli.go have been removed for optimization purposes.
    - **You can disable the auto-patch functionality in the installer while still being able to install Vencord without a UI.**
- Patch Vencord (and optionally OpenAsar) automatically, even through Discord updates
- Notifications are used to communicate success, failure, and errors

## Installation
Download and run INSTALLER.exe or INSTALLER from the latest release, depending on your OS.</br>
On macOS, you must run `chmod +x` to make the installer executable.</br>
All the required files will be downloaded for you.

## Building from Source
**You have much more control over your installation when building from source, including the Discord branch which is patched and whether or not to send notifications on success.**</br>
All original requirements for building the official installer apply here.</br>
Run install_[YOUR OPERATING SYSTEM].py to install BetterVencordPatch from source.</br>
To build from source, install Python 3.x and Go 1.25.x. The dependencies will be automatically installed.

## Credits
Auto-patcher created by [Aaron Wijesinghe](https://github.com/AaronWijesinghe)

This software uses a modified version of the [Vencord Installer](https://github.com/Vencord/Installer)</br>
Copyright (c) 2023 Vendicated and Vencord contributors</br>
Licensed under the GNU General Public License v3.0</br>
