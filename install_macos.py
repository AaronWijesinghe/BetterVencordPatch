import os
import platform
import shutil
import subprocess
import traceback

gold = "\033[0;33m"
end = "\033[0m"

paths = {
    "installer": "/Applications/VencordInstaller.app",
    "autopatcher": "/Applications/VencordInstaller.app/Contents/Resources/autovencordpatch",
    "autopatcher_plist": os.path.expanduser("~/Library/LaunchAgents/org.aaron.autovencordpatch.plist")
}

os.chdir(os.path.dirname(__file__))
def clear():
    print("\033[2J\033[3J\033[H", end='')

def install():
    clear()
    print(f"{gold}[BetterVencordPatch Installer (macOS)]{end}")
    print("This installer will install BetterVencordPatch from source.")
    branch = input("\nEnter the branch of Discord to be patched by Vencord (stable, ptb, canary): ")
    if branch not in ["stable", "ptb", "canary"]:
        input("This branch of Discord doesn't exist.")
        exit()
    openasar = input("Patch this branch of Discord with OpenAsar (y/N)? ").lower().strip() == "y"
    use_autopatch = input("Patch this branch of Discord through updates (y/N)? ").lower().strip() == "y"
    send_success_notifications = input("Send notifications on success (y/N)? ").lower().strip() == "y"

    clear()
    print(f"{gold}[Installing BetterVencordPatch]{end}")
    print(f"Installing with preferences: branch='{branch}', openasar={openasar}, use_autopatch={use_autopatch}, send_success_notifications={send_success_notifications}")
    print("\nRunning pre-install checks...", end=" ", flush=True)
    for dir in ["./autopatch/" if use_autopatch else "./installer/", "./installer/"]:
        if not os.path.exists(dir):
            print("failed")
            input(f"The directory '{dir}' is missing.")
            exit()
    print("done")

    os.chdir("./installer/")
    print("Building VencordInstaller.app...", end=" ", flush=True)
    subprocess.run(["go", "mod", "tidy"])
    subprocess.run(["go", "build", f"-ldflags=-X main.branch={branch} -X main.patchOpenAsar={str(openasar).lower()} -X main.sendSuccessNotifications={str(send_success_notifications).lower()}", "--tags", "cli"])
    subprocess.run(["mkdir", "-p", "VencordInstaller.app/Contents/MacOS"])
    subprocess.run(["mkdir", "-p", "VencordInstaller.app/Contents/Resources"])
    subprocess.run(["cp", "macos/Info.plist", "VencordInstaller.app/Contents/Info.plist"])
    subprocess.run(["mv", "VencordInstaller", "VencordInstaller.app/Contents/MacOS/VencordInstaller"])
    subprocess.run(["cp", "macos/icon.icns", "VencordInstaller.app/Contents/Resources/icon.icns"])
    subprocess.run(["rm", "-rf", os.path.pardir + "/VencordInstaller.app"])
    subprocess.run(["mv", "VencordInstaller.app", os.path.pardir + "/VencordInstaller.app"])
    print("done")

    if use_autopatch:
        print("Building auto-patch binary...", end=" ", flush=True)
        subprocess.run(["go", "mod", "tidy"])
        subprocess.run(["go", "build", f"-ldflags=-X main.branch={branch}", "--tags", "avp_macos", "-o", "autovencordpatch"])
        subprocess.run(["chmod", "+x", "autovencordpatch"])
        subprocess.run(["mv", "autovencordpatch", os.path.pardir + "/VencordInstaller.app/Contents/Resources/autovencordpatch"])
        print("done")

    os.chdir("../")
    subprocess.run(["rm", "-rf", "/Applications/VencordInstaller.app"])
    subprocess.run(["mv", "VencordInstaller.app", "/Applications/VencordInstaller.app"])

    if use_autopatch:
        uid = os.getuid()
        print("Running auto-patch install scripts...", end=" ", flush=True)
        subprocess.run(["cp", "autopatch/org.aaron.autovencordpatch.plist", paths["autopatcher_plist"]])
        subprocess.run(["chmod", "644", paths["autopatcher_plist"]])
        subprocess.run(["launchctl", "bootout", f"gui/{uid}", paths["autopatcher_plist"]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["launchctl", "bootstrap", f"gui/{uid}", paths["autopatcher_plist"]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["open", "/Applications/VencordInstaller.app"])
        print("done")

    input("\nSuccessfully installed BetterVencordPatch!")

def uninstall():
    clear()
    print(f"{gold}[BetterVencordPatch Installer (macOS)]{end}")
    input("Press ENTER to confirm uninstallation.")

    uid = os.getuid()
    if os.path.exists(paths["installer"]):
        shutil.rmtree(paths["installer"])
        print("\nRemoved the Vencord Installer")
    else:
        print("\nSkipped uninstalling the Vencord Installer as it doesn't exist")

    if os.path.exists(paths["autopatcher_plist"]):
        subprocess.run(["launchctl", "bootout", f"gui/{uid}", paths["autopatcher_plist"]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.remove(paths["autopatcher_plist"])
        print("Removed the autopatcher launchd plist")
    else:
        print("Skipped uninstalling the autopatcher launchd plist as it doesn't exist")

    input("\nSuccessfully uninstalled BetterVencordPatch!")

def main():
    if platform.system() != "Darwin":
        clear()
        print(f"{gold}[BetterVencordPatch Installer (macOS)]{end}")
        input("This operating system isn't supported by the installer.")
        exit()

    while True:
        clear()
        print(f"{gold}[BetterVencordPatch Installer (macOS)]{end}")
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
        print(f"{gold}[BetterVencordPatch Installer (macOS)]{end}")
        print("The installer has encountered a fatal error.")
        print("Please file an issue on GitHub if this error keeps appearing.\n")
        traceback.print_exc()
