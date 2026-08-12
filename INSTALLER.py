import os
import shutil
import zipfile
import getpass
import platform
import requests
from datetime import datetime
from sys import exit

gold = "\033[0;33m"
bold = "\033[1m"
end = "\033[0m"

os.chdir(os.path.dirname(__file__))
def clear():
    print("\033[2J\033[3J\033[H", end='')

def download_file(session, url):
    try:
        file_request = session.get(url)
        if not file_request.ok:
            raise requests.exceptions.ConnectionError
        return file_request.content
    except requests.exceptions.ConnectionError:
        input(f"Couldn't fetch file from URL: {url}")
        exit()

clear()
print(f"{bold}{gold}[BetterVencordPatch Installer]{end}")

try:
    releases_req = requests.get("https://api.github.com/repos/AaronWijesinghe/BetterVencordPatch/releases")
    if not releases_req.ok:
        raise requests.exceptions.ConnectionError
except requests.exceptions.ConnectionError:
    input("Couldn't fetch release data from GitHub.")
    exit()

releases = releases_req.json()
if len(releases) == 0:
    input("Release data is invalid. The installer cannot continue.")
    exit()

if "name" not in releases[0] or "published_at" not in releases[0]:
    input("Release data is invalid. The installer cannot continue.")
    exit()

bvp_version = releases[0]["name"]
published_timestamp = datetime.fromisoformat(releases[0]["published_at"])
print("This installer will download the latest files from GitHub Releases.")
print(f"Latest available version: {bvp_version} (released {published_timestamp})")
autopatch = input("\nAutomatically patch Discord with Vencord through updates (y/N)? ").lower().strip() == "y"
openasar = input("Patch OpenAsar (y/N)? ").lower().strip() == "y"

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
session = requests.Session()
print(f"{bold}{gold}[Downloading and moving required files...]{end}")
for asset in releases[0]["assets"]:
    if platform.system() == "Darwin":
        if f"VencordInstaller-{"no_" if not openasar else ""}openasar.app.zip" == asset["name"]:
            vi_app_darwin = download_file(session, asset["browser_download_url"])
            open("VencordInstaller.app.zip", "wb").write(vi_app_darwin)
            if os.path.exists("/Applications/VencordInstaller.app"):
                shutil.rmtree("/Applications/VencordInstaller.app")
            try:
                with zipfile.ZipFile("VencordInstaller.app.zip", 'r') as zip_ref:
                    zip_ref.extractall("/Applications/")
            except:
                os.system("rm -rf /Applications/VencordInstaller.app")
                os.system("rm -rf VencordInstaller.app.zip")
                input("Failed to extract the Vencord Installer.")
                exit()
            shutil.move(f"/Applications/VencordInstaller-{"no_" if not openasar else ""}openasar.app", "/Applications/VencordInstaller.app")
            os.system("chmod +x /Applications/VencordInstaller.app/Contents/MacOS/vencordinstaller")
            os.remove("VencordInstaller.app.zip")
            print(f"Successfully downloaded BetterVencordPatch")
    elif platform.system() == "Windows":
        if f"VencordInstaller-{"no_" if not openasar else ""}openasar.exe" == asset["name"]:
            vi_app_win = download_file(session, asset["browser_download_url"])
            open(f"C:/Users/{getpass.getuser()}/AppData/Local/BetterVencordPatch/vencordinstaller.exe", "wb").write(vi_app_win)
            print(f"Successfully downloaded BetterVencordPatch")
        elif f"autovencordpatch.exe" == asset["name"] and autopatch:
            autopatch_win = download_file(session, asset["browser_download_url"])
            open(f"C:/Users/{getpass.getuser()}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/autovencordpatch.exe", "wb").write(autopatch_win)
            print(f"Successfully installed autopatch component")

if platform.system() == "Darwin" and autopatch:
    for asset in releases[0]["assets"]:
        if asset["name"] == "org.aaron.autovencordpatch.plist":
            autopatch_plist = download_file(session, asset["browser_download_url"])
            open(f"/Users/{getpass.getuser()}/Library/LaunchAgents/org.aaron.autovencordpatch.plist", "wb").write(autopatch_plist)
            os.system("chmod 644 ~/Library/LaunchAgents/org.aaron.autovencordpatch.plist")
            os.system("launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/org.aaron.autovencordpatch.plist 2>&1")
            os.system("launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/org.aaron.autovencordpatch.plist 2>&1")
            print(f"Successfully installed autopatch launchd plist (macOS)")
        elif asset["name"] == "autovencordpatch":
            autopatch_darwin = download_file(session, asset["browser_download_url"])
            open(f"/Applications/VencordInstaller.app/Contents/Resources/autovencordpatch", "wb").write(autopatch_darwin)
            os.system("chmod +x /Applications/VencordInstaller.app/Contents/Resources/autovencordpatch")
            print(f"Successfully installed autopatch component")
    os.system("open /Applications/VencordInstaller.app")

session.close()
print("\nSuccessfully installed BetterVencordPatch!")
if platform.system() == "Windows" and autopatch == True:
    input("Make sure to restart your computer so the auto-patcher can run.")
else:
    input("Press ENTER to exit.")
exit()
