import os
import platform
import shutil
import subprocess
import traceback

gold = "\033[0;33m"
end = "\033[0m"

paths = {
    "installer": os.path.expanduser("~\\AppData\\Local\\BetterVencordPatch\\vencordinstaller.exe"),
    "autopatcher": os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\autovencordpatch.exe"),
    "bvp_dir": os.path.expanduser("~\\AppData\\Local\\BetterVencordPatch\\")
}

os.chdir(os.path.dirname(__file__))
def clear():
    print("\033[2J\033[3J\033[H", end='')

def install():
    clear()
    print(f"{gold}[BetterVencordPatch Installer (Windows)]{end}")
    branch = input("Enter the branch of Discord to be patched by Vencord (stable, ptb, canary): ")
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
    os.makedirs(paths["bvp_dir"], exist_ok=True)
    if platform.system() != "Windows":
        print("failed")
        input("This operating system is not supported by this installer.")
        exit()
    for dir in ["./autopatch/" if use_autopatch else "./installer/"]:
        if not os.path.exists(dir):
            print("failed")
            input(f"The directory '{dir}' is missing.")
            exit()
    print("done")

    branch_suffixes = {
        "stable": "",
        "ptb": "PTB",
        "canary": "Canary"
    }
    os.chdir("./installer/")
    print("Building VencordInstaller.exe...", end=" ", flush=True)
    subprocess.run(["go", "mod", "tidy"])
    subprocess.run(["go", "build", f"-ldflags=-H=windowsgui -X main.branch={branch} -X main.patchOpenAsar={str(openasar).lower()} -X main.sendSuccessNotifications={str(send_success_notifications).lower()}", "--tags", "cli"])
    if os.path.exists(paths["installer"]):
        os.remove(paths["installer"])
    os.rename("vencordinstaller.exe", paths["autopatcher"])
    print("done")

    if use_autopatch:
        print("Building auto-patch binary...", end=" ", flush=True)
        subprocess.run(["go", "mod", "tidy"])
        subprocess.run(["go", "build", f"-ldflags=-H=windowsgui -X main.branch={branch_suffixes[branch]}", "--tags", "avp_win", "-o", "autovencordpatch.exe"])
        # uncomment this line and comment the line above to see autopatcher output
        # subprocess.run(["go", "build", f"-X main.branch={branch_suffixes[branch]}", "--tags", "avp_win", "-o", "autovencordpatch.exe"])
        subprocess.run(["taskkill", "/f", "/im", "autovencordpatch.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["taskkill", "/f", "/im", "vencordinstaller.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(paths["autopatcher"]):
            os.remove(paths["autopatcher"])
        os.rename("autovencordpatch.exe", paths["autopatcher"])
        print("done")

    input("\nSuccessfully installed BetterVencordPatch!")

def uninstall():
    clear()
    print(f"{gold}[BetterVencordPatch Installer (Windows)]{end}")
    input("Press ENTER to confirm uninstallation.")

    subprocess.run(["taskkill", "/f", "/im", "autovencordpatch.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["taskkill", "/f", "/im", "vencordinstaller.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("\nStopped running processes")

    if os.path.exists(paths["bvp_dir"]):
        shutil.rmtree(paths["bvp_dir"])
        print("Removed the Vencord Installer")
    else:
        print("Skipped uninstalling the Vencord Installer as it doesn't exist")

    if os.path.exists(paths["autopatcher"][op]):
        os.remove(paths["autopatcher"][op])
        print("Removed the autopatcher")
    else:
        print("Skipped uninstalling the autopatcher as it doesn't exist")

    input("\nSuccessfully uninstalled BetterVencordPatch!")

def main():
    while True:
        clear()
        print(f"{gold}[BetterVencordPatch Installer (Windows)]{end}")
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
        print(f"{gold}[BetterVencordPatch Installer (Windows)]{end}")
        print("The installer has encountered a fatal error.")
        print("Please file an issue on GitHub if this error keeps appearing.\n")
        traceback.print_exc()