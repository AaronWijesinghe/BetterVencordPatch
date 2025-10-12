import os
import json
import getpass
import platform
import requests

suffix = ".app" if platform.system() == "Darwin" else ".exe"
os.chdir(os.path.dirname(__file__))
def clear():
    os.system("cls" if platform.system() == "Windows" else "clear;clear")

clear()
print("[BetterVencordPatch Installer]")
print("This installer will download the latest files from GitHub.")
print("")
autopatch = input("Automatically patch Discord with Vencord through updates? ").lower().strip() == "y"
openasar = input("Patch OpenAsar (y/n)? ").lower().strip() == "y"

os.chdir(os.path.dirname(__file__))
releases = requests.get("https://api.github.com/repos/introvertednoob/bettervencordpatch/releases")
if not releases.ok:
    print("Couldn't fetch releases. Exiting...")
    exit()

paths = {
    "Windows": [
        f"C:/Users/{getpass.getuser()}/AppData/Local/BetterVencordPatch/vencordinstaller.exe",
        f"C:/Users/{getpass.getuser()}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/autovencordpatch.exe",
    ],
    "Darwin": [
        f"/Applications/VencordInstaller.app",
        f"/Applications/VencordInstaller.app/Contents/Resources/autovencordpatch",
    ],
}

clear()
print("[Downloading required files...]")
rel = json.loads(releases.text)
for asset in rel[0]["assets"]:
    if f"VencordInstaller-{"no_" if not openasar else ""}openasar.exe" in asset["browser_download_url"] and platform.system() == "Windows":
        open(paths[platform.system()][0], "wb").write(requests.get(asset["browser_download_url"]).content)
        print(f"Successfully downloaded BetterVencordPatch")
    elif f"VencordInstaller-{"no_" if not openasar else ""}openasar.app" in asset["browser_download_url"] and platform.system() == "Darwin":
        open("VencordInstaller.app.zip", "wb").write(requests.get(asset["browser_download_url"]).content)
        # TODO: add .zip unzipping code here for .app files
        # TODO: move extracted app to paths[platform.system()][0]
        print(f"Successfully downloaded BetterVencordPatch")
    elif f"autovencordpatch{".exe" if platform.system() == "Windows" else ""}" in asset["browser_download_url"] and autopatch:
        open(paths[platform.system()][1], "wb").write(requests.get(asset["browser_download_url"]).content)
        print(f"Successfully installed autopatch component")
    elif "org.aaron.autovencordpatch.plist" in asset["browser_download_url"] and platform.system() == "Darwin":
        open(f"~/Library/LaunchAgents/org.aaron.autovencordpatch.plist", "wb").write(requests.get(asset["browser_download_url"]).content)
        print(f"Successfully installed autopatch plist (macOS)")