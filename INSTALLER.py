import os
import shutil
import zipfile
import platform
import requests
import traceback
import subprocess
from datetime import datetime
from sys import exit

gold = "\033[0;33m"
end = "\033[0m"

paths = {
    "installer": {
        "Windows": os.path.expanduser("~\\AppData\\Local\\BetterVencordPatch\\vencordinstaller.exe"),
        "Darwin": "/Applications/VencordInstaller.app"
    },
    "autopatcher": {
        "Windows": os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\autovencordpatch.exe"),
        "Darwin": "/Applications/VencordInstaller.app/Contents/Resources/autovencordpatch"
    },
    "autopatcher_plist": os.path.expanduser("~/Library/LaunchAgents/org.aaron.autovencordpatch.plist")
}

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

def install():
    clear()
    print(f"{gold}[BetterVencordPatch Installer]{end}")

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

    op = platform.system()
    bvp_version = releases[0]["name"]
    published_timestamp = datetime.fromisoformat(releases[0]["published_at"])
    print("This installer will download the latest files from GitHub Releases.")
    print(f"Latest available version: {bvp_version} (released {published_timestamp})")
    autopatch = input("\nAutomatically patch Discord with Vencord through updates (y/N)? ").lower().strip() == "y"
    openasar = input("Patch OpenAsar (y/N)? ").lower().strip() == "y"

    if op == "Windows":
        subprocess.run(["taskkill", "/f", "/im", "autovencordpatch.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["taskkill", "/f", "/im", "vencordinstaller.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        bvp_path = os.path.expanduser("~/AppData/Local/BetterVencordPatch/")
        os.makedirs(bvp_path, exist_ok=True)

    clear()
    session = requests.Session()
    print(f"{gold}[Downloading and moving required files...]{end}")
    for asset in releases[0]["assets"]:
        if op == "Darwin":
            if f"VencordInstaller-{"no_" if not openasar else ""}openasar.app.zip" == asset["name"]:
                vi_app_darwin = download_file(session, asset["browser_download_url"])
                open("VencordInstaller.app.zip", "wb").write(vi_app_darwin)
                if os.path.exists("/Applications/VencordInstaller.app"):
                    shutil.rmtree("/Applications/VencordInstaller.app")
                try:
                    with zipfile.ZipFile("VencordInstaller.app.zip", 'r') as zip_ref:
                        zip_ref.extractall("/Applications/")
                except:
                    subprocess.run(["rm", "-rf", paths["installer"][op]])
                    subprocess.run(["rm", "-rf", "VencordInstaller.app.zip"])
                    input("Failed to extract the Vencord Installer.")
                    exit()
                shutil.move(f"/Applications/VencordInstaller-{"no_" if not openasar else ""}openasar.app", paths["installer"][op])
                subprocess.run(["chmod", "+x", "/Applications/VencordInstaller.app/Contents/MacOS/vencordinstaller"])
                os.remove("VencordInstaller.app.zip")
                print(f"Downloaded BetterVencordPatch")
        elif op == "Windows":
            if f"VencordInstaller-{"no_" if not openasar else ""}openasar.exe" == asset["name"]:
                vi_app_path = os.path.expanduser("~/AppData/Local/BetterVencordPatch/vencordinstaller.exe")
                vi_app_win = download_file(session, asset["browser_download_url"])
                open(vi_app_path, "wb").write(vi_app_win)
                print(f"Downloaded BetterVencordPatch")
            elif f"autovencordpatch.exe" == asset["name"] and autopatch:
                autopatch_win = download_file(session, asset["browser_download_url"])
                open(paths["autopatcher"][op], "wb").write(autopatch_win)
                print(f"Installed autopatch component")

    if op == "Darwin" and autopatch:
        for asset in releases[0]["assets"]:
            if asset["name"] == "org.aaron.autovencordpatch.plist":
                uid = os.getuid()
                autopatch_plist = download_file(session, asset["browser_download_url"])
                open(paths["autopatcher_plist"], "wb").write(autopatch_plist)
                subprocess.run(["chmod", "644", paths["autopatcher_plist"]])
                subprocess.run(["launchctl", "bootout", f"gui/{uid}", paths["autopatcher_plist"]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(["launchctl", "bootstrap", f"gui/{uid}", paths["autopatcher_plist"]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"Installed autopatch launchd plist (macOS)")
            elif asset["name"] == "autovencordpatch":
                autopatch_darwin = download_file(session, asset["browser_download_url"])
                open(f"/Applications/VencordInstaller.app/Contents/Resources/autovencordpatch", "wb").write(autopatch_darwin)
                subprocess.run(["chmod", "+x", "/Applications/VencordInstaller.app/Contents/Resources/autovencordpatch"])
                print(f"Installed autopatch component")
        subprocess.run(["open", "/Applications/VencordInstaller.app"])

    if not autopatch:
        print("Skipped installing the autopatcher")

    session.close()
    print("\nSuccessfully installed BetterVencordPatch!")
    if op == "Windows" and autopatch == True:
        os.startfile(paths["autopatcher"][op])
    input("Press ENTER to return to the main menu.")

def uninstall():
    clear()
    print(f"{gold}[BetterVencordPatch Uninstaller]{end}")
    input("Press ENTER to confirm uninstallation.")

    op = platform.system()
    if op == "Darwin":
        uid = os.getuid()
        if os.path.exists(paths["installer"][op]):
            shutil.rmtree(paths["installer"][op])
            print("\nRemoved the Vencord Installer")
        else:
            print("\nSkipped uninstalling the Vencord Installer as it doesn't exist")

        if os.path.exists(paths["autopatcher_plist"]):
            subprocess.run(["launchctl", "bootout", f"gui/{uid}", paths["autopatcher_plist"]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.remove(paths["autopatcher_plist"])
            print("Removed the autopatcher launchd plist")
        else:
            print("Skipped uninstalling the autopatcher launchd plist as it doesn't exist")
    elif op == "Windows":
        subprocess.run(["taskkill", "/f", "/im", "autovencordpatch.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["taskkill", "/f", "/im", "vencordinstaller.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("\nStopped running processes")

        if os.path.exists(paths["installer"][op]):
            shutil.rmtree(f"{paths["installer"][op]}/..")
            print("Removed the Vencord Installer")
        else:
            print("Skipped uninstalling the Vencord Installer as it doesn't exist")

        if os.path.exists(paths["autopatcher"][op]):
            os.remove(paths["autopatcher"][op])
            print("Removed the autopatcher")
        else:
            print("Skipped uninstalling the autopatcher as it doesn't exist")
    else:
        input("The uninstaller is not supported on your operating system.")

    input("\nSuccessfully uninstalled BetterVencordPatch!")

def main():
    while True:
        clear()
        print(f"{gold}[BetterVencordPatch Installer]{end}")
        print("Choose an option below:")
        print("[1] Install BetterVencordPatch")
        print("[2] Uninstall BetterVencordPatch")
        print("[3] Exit")

        choice = input("\n> ")
        match choice:
            case "1":
                install()
            case "2":
                uninstall()
            case "3":
                exit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        clear()
        print(f"{gold}[BetterVencordPatch Installer]{end}")
        print("The installer has encountered a fatal error.")
        print("Please file an issue on GitHub if this error keeps appearing.\n")
        traceback.print_exc()
