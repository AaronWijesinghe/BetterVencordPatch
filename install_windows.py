import os
import getpass
import platform

os.chdir(os.path.dirname(__file__))
def clear():
    os.system("cls")

clear()
print("[BetterVencordPatch Installer (Windows)]")
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
os.makedirs(f"C:/Users/{getpass.getuser()}/AppData/Local/bettervencordpatch/", exist_ok=True)
if platform.system() != "Windows":
    print("failed")
    input("This operating system is not supported by this installer. ")
    exit()
for dir in ["./autopatch/" if use_autopatch else "./installer/"]:
    if not os.path.exists(dir):
        print("failed")
        input(f"The directory '{dir}' is missing. ")
        exit()
print("done")

branch_suffixes = {
    "stable": "",
    "ptb": "PTB",
    "canary": "Canary"
}
os.chdir("./installer/")
print("Building VencordInstaller.exe...", end=" ", flush=True)
os.system("go mod tidy")
os.system("set CGO_ENABLED=0")
os.system("set GOOS=windows")
os.system("set GOARCH=amd64")
os.system(f"go build -ldflags=\"-H=windowsgui -X vencordinstaller.pyBranch='{branch}' -X vencordinstaller.pyOpenAsar='{openasar}' -X vencordinstaller.pySendSuccessNotifications='{send_success_notifications}'\" --tags cli")
if os.path.exists(f"C:/Users/{getpass.getuser()}/AppData/Local/bettervencordpatch/vencordinstaller.exe"):
    os.remove(f"C:/Users/{getpass.getuser()}/AppData/Local/bettervencordpatch/vencordinstaller.exe")
os.rename("vencordinstaller.exe", f"C:/Users/{getpass.getuser()}/AppData/Local/bettervencordpatch/vencordinstaller.exe")
print("done")

if use_autopatch:
    print("Building auto-patch binary...", end=" ", flush=True)
    os.system("go mod tidy")
    #os.system(f"go build -ldflags=\"-H=windowsgui -X vencordinstaller.discordBranchSuffix='{branch_suffixes[branch]}'\" --tags avp_win -o autovencordpatch.exe")
    # debug
    os.system(f"go build -ldflags=\"-X vencordinstaller.discordBranchSuffix='{branch_suffixes[branch]}'\" --tags avp_win -o autovencordpatch.exe")
    os.system("taskkill /f /im autovencordpatch.exe >NUL 2>&1")
    if os.path.exists(f"C:/Users/{getpass.getuser()}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/autovencordpatch.exe"):
        os.remove(f"C:/Users/{getpass.getuser()}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/autovencordpatch.exe")
    os.rename("autovencordpatch.exe", f"C:/Users/{getpass.getuser()}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/autovencordpatch.exe")
    os.system(f"\"C:/Users/{getpass.getuser()}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/autovencordpatch.exe\"")
    print("done")

input("\nSuccessfully installed BetterVencordPatch! ")