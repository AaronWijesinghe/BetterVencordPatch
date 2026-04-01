[0.2.0]
- Fixed an issue where BVP would send a push "Failed to patch Vencord" notification when more specific notifications could be sent
    - If Discord was unpatched and the Full Disk Access/App Management permissions were disabled for VencordInstaller.app, the above issue occured.