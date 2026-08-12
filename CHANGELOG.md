### Version 0.5.0
**You must redownload INSTALLER/INSTALLER.exe.**<br>
Updates have been made to the installer that aren't present in prior versions.
- [#9, Lani0516](https://github.com/AaronWijesinghe/BetterVencordPatch/pull/9) - Verify SHA-256 of downloaded assets before installing them
- [#10, Lani0516](https://github.com/AaronWijesinghe/BetterVencordPatch/pull/10) - Make sure Vencord updates when Discord updates
- Improved the formatting of the installer with ANSI formatting (711efac)
- Replaced the clear() function of the installer with a non-OS-specific clear() function (148eaa9)
- Give the right permissions to the macOS launchd .plist file when installing BetterVencordPatch (802b828)
- Show the version of BetterVencordPatch that will be installed (f2c978b)
- Show the date and time of the latest release within INSTALLER (1f8c067)

### Version 0.4.2
- Fixed an issue where Vencord wouldn't patch when choosing to patch OpenAsar
- Show a permission error dialog if OpenAsar can't be patched
- Refactored Vencord installer arguments to remove the prefix "py"
- Discord branch suffixes are now stored within .go files (Windows)
- Discord app names are now stored within .go files (macOS)

### Version 0.4.1
- Fixed an issue where injected variables (such as branch, sending success notifications, and OpenAsar installation) wouldn't take effect even if their respective options were changed

### Version 0.4.0
- [#4, v81d](https://github.com/AaronWijesinghe/BetterVencordPatch/pull/4) - Show yes/no prompt defaults in all installers
- Attempted to fix Windows auto-patching
    - The autopatcher now scans for Discord.ico updates, since this file always gets overwritten when an update occurs
- Added redundancy to the macOS autopatcher
    - Instead of solely relying on write events to build_info.json, the app.asar file is not also checked

### Version 0.3.0
- Removed the use of notify() in patcher.go, instead using Go's built-in error system
- "Silent" errors are now displayed to the user

### Version 0.2.0
- Fixed an issue where BVP would send a push "Failed to patch Vencord" notification when more specific notifications could be sent
    - If Discord was unpatched and the Full Disk Access/App Management permissions were disabled for VencordInstaller.app, the above issue occured.