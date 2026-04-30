import os
import json
import shutil
import zipfile
import getpass
import platform
import requests
from sys import exit
from pathlib import Path
import subprocess

os.chdir(os.path.dirname(__file__))
def clear():
    os.system("cls" if platform.system() == "Windows" else "clear;clear")

def get_windows_paths():
    local_app_data = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    app_data = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    install_dir = local_app_data / "BetterVencordPatch"
    startup_dir = app_data / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"

    return [
        install_dir / "vencordinstaller.exe",
        startup_dir / "autovencordpatch.exe",
    ]

clear()
print("[BetterVencordPatch Installer]")
print("This installer will download the latest files from GitHub.")
print("")
autopatch = input("Automatically patch Discord with Vencord through updates (y/N)? ").lower().strip() == "y"
openasar = input("Patch OpenAsar (y/N)? ").lower().strip() == "y"

releases = requests.get("https://api.github.com/repos/introvertednoob/bettervencordpatch/releases")
if not releases.ok:
    print("\nCouldn't fetch releases. Exiting...")
    exit()

paths = {
    "Windows": get_windows_paths(),
    "Darwin": [
        f"/Applications/VencordInstaller.app",
        f"/Applications/VencordInstaller.app/Contents/Resources/autovencordpatch",
    ],
}

if platform.system() == "Windows":
    os.system("taskkill /f /im autovencordpatch.exe >NUL 2>&1")
    paths["Windows"][0].parent.mkdir(parents=True, exist_ok=True)
    paths["Windows"][1].parent.mkdir(parents=True, exist_ok=True)

clear()
print("[Downloading and moving required files...]")
rel = json.loads(releases.text)
for asset in rel[0]["assets"]:
    if platform.system() == "Darwin":
        if f"VencordInstaller-{"no_" if not openasar else ""}openasar.app.zip" == asset["name"]:
            open("VencordInstaller.app.zip", "wb").write(requests.get(asset["browser_download_url"]).content)
            if os.path.exists("/Applications/VencordInstaller.app"):
                shutil.rmtree("/Applications/VencordInstaller.app")
            with zipfile.ZipFile("VencordInstaller.app.zip", 'r') as zip_ref:
                zip_ref.extractall("/Applications/")
            shutil.move(f"/Applications/VencordInstaller-{"no_" if not openasar else ""}openasar.app", "/Applications/VencordInstaller.app")
            os.system("chmod +x /Applications/VencordInstaller.app/Contents/MacOS/vencordinstaller")
            os.remove("VencordInstaller.app.zip")
            print(f"Successfully downloaded BetterVencordPatch")
    elif platform.system() == "Windows":
        if f"VencordInstaller-{"no_" if not openasar else ""}openasar.exe" == asset["name"]:
            open(paths["Windows"][0], "wb").write(requests.get(asset["browser_download_url"]).content)
            print(f"Successfully downloaded BetterVencordPatch")
        elif f"autovencordpatch.exe" == asset["name"] and autopatch:
            open(paths["Windows"][1], "wb").write(requests.get(asset["browser_download_url"]).content)
            print(f"Successfully installed autopatch component")

if platform.system() == "Darwin":
    for asset in rel[0]["assets"]:
        if asset["name"] == "org.aaron.autovencordpatch.plist":
            open(f"/Users/{getpass.getuser()}/Library/LaunchAgents/org.aaron.autovencordpatch.plist", "wb").write(requests.get(asset["browser_download_url"]).content)
            print(f"Successfully installed autopatch launchd plist (macOS)")
        elif asset["name"] == "autovencordpatch" and autopatch:
            open(f"/Applications/VencordInstaller.app/Contents/Resources/autovencordpatch", "wb").write(requests.get(asset["browser_download_url"]).content)
            os.system("chmod +x /Applications/VencordInstaller.app/Contents/Resources/autovencordpatch")
            print(f"Successfully installed autopatch component")
    os.system("open /Applications/VencordInstaller.app")

if platform.system() == "Windows":
    print("\n[Patching Discord with Vencord...]")
    result = subprocess.run([str(paths["Windows"][0])])
    if result.returncode != 0:
        input("Failed to patch Discord with Vencord. ")
        exit(result.returncode)

print("\nSuccessfully installed BetterVencordPatch!")
input("If you're on Windows and installed the auto-patcher, make sure to restart your computer so the auto-patcher can run. ")
exit()
