import os
import platform

os.chdir(os.path.dirname(__file__))
def clear():
    for i in range(2):
        os.system("clear")

def run_sh(sh):
    for cmd in sh.split("\n"):
        os.system(f"{cmd}")

clear()
print("[BetterVencordPatch Installer (macOS)]")
branch = input("Enter the branch of Discord to be patched by Vencord (stable, ptb, canary): ")
if branch not in ["stable", "ptb", "canary"]:
    input("This branch of Discord doesn't exist. ")
    exit()
openasar = input("Patch this branch of Discord with OpenAsar (y/N)? ").lower().strip() == "y"
use_autopatch = input("Patch this branch of Discord through updates (y/N)? ").lower().strip() == "y"
send_success_notifications = input("Send notifications on success (y/N)? ").lower().strip() == "y"

clear()
print("[Installing BetterVencordPatch]")
print(f"Installing with preferences: branch='{branch}', openasar={openasar}, use_autopatch={use_autopatch}, send_success_notifications={send_success_notifications}")
print("\nRunning pre-install checks...", end=" ", flush=True)
if platform.system() != "Darwin":
    print("failed")
    input("This operating system is not supported by this installer. ")
    exit()
for dir in ["./autopatch/" if use_autopatch else "./installer/", "./installer/"]:
    if not os.path.exists(dir):
        print("failed")
        input(f"The directory '{dir}' is missing. ")
        exit()
print("done")

discords = {
    "stable": "Discord.app",
    "ptb": "Discord PTB.app",
    "canary": "Discord Canary.app"
}

os.chdir("./installer/")
build_vi = f"""
go mod tidy
CGO_ENABLED=0 go build -ldflags=\"-X vencordinstaller.pyBranch='{branch}' -X vencordinstaller.pyOpenAsar='{openasar}' -X vencordinstaller.pySendSuccessNotifications='{send_success_notifications}'\" --tags cli
mkdir -p VencordInstaller.app/Contents/MacOS
mkdir -p VencordInstaller.app/Contents/Resources
cp macos/Info.plist VencordInstaller.app/Contents/Info.plist
mv VencordInstaller VencordInstaller.app/Contents/MacOS/VencordInstaller
cp macos/icon.icns VencordInstaller.app/Contents/Resources/icon.icns
rm -rf ../VencordInstaller.app
mv VencordInstaller.app ../VencordInstaller.app
"""
print("Building VencordInstaller.app...", end=" ", flush=True)
run_sh(build_vi)
print("done")

if use_autopatch:
    print("Building auto-patch binary...", end=" ", flush=True)
    build_avp = f"""
    go mod tidy
    CGO_ENABLED=0 go build -ldflags=\"-X vencordinstaller.discordAppName='{discords[branch]}'\" --tags avp_macos -o autovencordpatch
    chmod +x autovencordpatch
    mv autovencordpatch ../VencordInstaller.app/Contents/Resources/autovencordpatch
    """
    run_sh(build_avp)
    print("done")

os.chdir("../")
mv_to_applications = """
rm -rf /Applications/VencordInstaller.app
mv VencordInstaller.app /Applications/VencordInstaller.app
"""
run_sh(mv_to_applications)

if use_autopatch:
    print("Running auto-patch install scripts...", end=" ", flush=True)
    install = """
    cp autopatch/org.aaron.autovencordpatch.plist ~/Library/LaunchAgents/org.aaron.autovencordpatch.plist
    launchctl unload ~/Library/LaunchAgents/org.aaron.autovencordpatch.plist > /dev/null 2>&1
    launchctl load ~/Library/LaunchAgents/org.aaron.autovencordpatch.plist > /dev/null 2>&1
    open /Applications/VencordInstaller.app
    """
    run_sh(install)
    print("done")

input("\nSuccessfully installed BetterVencordPatch! ")
