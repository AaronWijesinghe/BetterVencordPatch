import os
import json
import shutil
import zipfile
import getpass
import platform
import requests
from sys import exit

gold = "\033[0;33m"
bold = "\033[1m"
end = "\033[0m"

os.chdir(os.path.dirname(__file__))
def clear():
    print("\033[2J\033[3J\033[H", end='')

clear()
print(f"{bold}{gold}[BetterVencordPatch Installer]{end}")
print("This installer will download the latest files from GitHub.")
print("")
autopatch = input("Automatically patch Discord with Vencord through updates (y/N)? ").lower().strip() == "y"
openasar = input("Patch OpenAsar (y/N)? ").lower().strip() == "y"

releases = requests.get("https://api.github.com/repos/introvertednoob/bettervencordpatch/releases")
if not releases.ok:
    print("\nCouldn't fetch releases. Exiting...")
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

if platform.system() == "Windows":
    os.system("taskkill /f /im autovencordpatch.exe >NUL 2>&1")
    os.makedirs(f"C:/Users/{getpass.getuser()}/AppData/Local/BetterVencordPatch/", exist_ok=True)

clear()
print(f"{bold}{gold}[Downloading and moving required files...]{end}")
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
            open(f"C:/Users/{getpass.getuser()}/AppData/Local/BetterVencordPatch/vencordinstaller.exe", "wb").write(requests.get(asset["browser_download_url"]).content)
            print(f"Successfully downloaded BetterVencordPatch")
        elif f"autovencordpatch.exe" == asset["name"] and autopatch:
            open(f"C:/Users/{getpass.getuser()}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/autovencordpatch.exe", "wb").write(requests.get(asset["browser_download_url"]).content)
            print(f"Successfully installed autopatch component")

if platform.system() == "Darwin":
    for asset in rel[0]["assets"]:
        if asset["name"] == "org.aaron.autovencordpatch.plist":
            open(f"/Users/{getpass.getuser()}/Library/LaunchAgents/org.aaron.autovencordpatch.plist", "wb").write(requests.get(asset["browser_download_url"]).content)
            os.system("chmod 644 ~/Library/LaunchAgents/org.aaron.autovencordpatch.plist")
            print(f"Successfully installed autopatch launchd plist (macOS)")
        elif asset["name"] == "autovencordpatch" and autopatch:
            open(f"/Applications/VencordInstaller.app/Contents/Resources/autovencordpatch", "wb").write(requests.get(asset["browser_download_url"]).content)
            os.system("chmod +x /Applications/VencordInstaller.app/Contents/Resources/autovencordpatch")
            print(f"Successfully installed autopatch component")
    os.system("open /Applications/VencordInstaller.app")

print("\nSuccessfully installed BetterVencordPatch!")
if platform.system() == "Windows" and autopatch == True:
    input("Make sure to restart your computer so the auto-patcher can run.")
else:
    input("Press ENTER to exit.")
exit()
