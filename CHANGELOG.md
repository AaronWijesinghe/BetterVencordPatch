### Version 0.3.0
- Removed the use of notify() in patcher.go, instead using Go's built-in error system
- "Silent" errors are now displayed to the user

### Version 0.2.0
- Fixed an issue where BVP would send a push "Failed to patch Vencord" notification when more specific notifications could be sent
    - If Discord was unpatched and the Full Disk Access/App Management permissions were disabled for VencordInstaller.app, the above issue occured.