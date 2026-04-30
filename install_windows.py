import os
import platform
from pathlib import Path

os.chdir(os.path.dirname(__file__))
def clear():
    os.system("cls")

local_app_data = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
app_data = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
install_dir = local_app_data / "bettervencordpatch"
installer_path = install_dir / "vencordinstaller.exe"
startup_dir = app_data / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
autopatch_path = startup_dir / "autovencordpatch.exe"

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
install_dir.mkdir(parents=True, exist_ok=True)
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
os.system(f"go build -ldflags=\"-H=windowsgui -X main.branch={branch} -X main.patchOpenAsar={str(openasar).lower()} -X main.sendSuccessNotifications='{str(send_success_notifications).lower()}'\" --tags cli")
if installer_path.exists():
    installer_path.unlink()
os.rename("vencordinstaller.exe", installer_path)
print("done")

if use_autopatch:
    print("Building auto-patch binary...", end=" ", flush=True)
    os.system("go mod tidy")
    os.system(f"go build -ldflags=\"-H=windowsgui -X main.branch={branch_suffixes[branch]}\" --tags avp_win -o autovencordpatch.exe")
    # uncomment this line and comment the line above to see autopatcher output
    # os.system(f"go build -ldflags=\"-X main.branch={branch_suffixes[branch]}\" --tags avp_win -o autovencordpatch.exe")
    os.system("taskkill /f /im autovencordpatch.exe >NUL 2>&1")
    startup_dir.mkdir(parents=True, exist_ok=True)
    if autopatch_path.exists():
        autopatch_path.unlink()
    os.rename("autovencordpatch.exe", autopatch_path)
    print("done")

input("\nSuccessfully installed BetterVencordPatch! ")