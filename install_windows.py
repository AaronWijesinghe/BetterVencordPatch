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
openasar = input("Patch this branch of Discord with OpenAsar (y/n)? ").lower().strip() == "y"
use_autopatch = input("Patch this branch of Discord through updates (y/n)? ").lower().strip() == "y"
send_success_notifications = input("Send notifications on success (y/n)? ").lower().strip() == "y"

clear()
print("[Installing BetterVencordPatch]")
print(f"Installing with preferences: branch='{branch}', openasar={openasar}, use_autopatch={use_autopatch}, send_success_notifications={send_success_notifications}")
print("\nRunning pre-install checks...", end=" ", flush=True)
if platform.system() != "Windows":
    print("failed")
    input("This operating system is not supported by this installer. ")
    exit()
for dir in ["./files/", "./autopatch/" if use_autopatch else "./files/", "./installer/"]:
    if not os.path.exists(dir):
        print("failed")
        input(f"The directory '{dir}' is missing. ")
        exit()
for file in ["./files/autovencordpatch.go" if use_autopatch else "./files/cli.go", "./files/cli.go"]:
    if not os.path.exists(file):
        print("failed")
        input(f"The file '{file}' is missing. ")
        exit()
print("done")

discords = {
    "stable": "Discord/",
    "ptb": "DiscordPTB/",
    "canary": "DiscordCanary/"
}
print("Preparing install environment...", end=" ", flush=True)
if use_autopatch:
    avp_code = open("./files/autovencordpatch_win.go", "r").read()
    avp_code = avp_code.replace("Discord/", discords[branch])
    open("./autopatch/autovencordpatch.go", "w").write(avp_code)
cli_code = open("./files/cli.go", "r").read()
cli_code = cli_code.replace("var pyOpenAsar = false", f"var pyOpenAsar = {str(openasar).lower()}")
cli_code = cli_code.replace("var pyBranch = \"stable\"", f"var pyBranch = \"{branch}\"")
cli_code = cli_code.replace("var pySendSuccessNotifications = true", f"var pySendSuccessNotifications = {str(send_success_notifications).lower()}")
open("./installer/cli.go", "w").write(cli_code)
print("done")

os.chdir("./installer/")
print("Building VencordInstaller.exe...", end=" ", flush=True)
os.system("go mod tidy")
os.system("set CGO_ENABLED=0")
os.system("set GOOS=windows")
os.system("set GOARCH=amd64")
os.system("go build -ldflags=\"-H=windowsgui\" --tags cli")
if os.path.exists(f"C:/Users/{getpass.getuser()}/AppData/Local/bettervencordpatch/vencordinstaller.exe"):
    os.remove(f"C:/Users/{getpass.getuser()}/AppData/Local/bettervencordpatch/vencordinstaller.exe")
os.rename("vencordinstaller.exe", f"C:/Users/{getpass.getuser()}/AppData/Local/bettervencordpatch/vencordinstaller.exe")
print("done")

if use_autopatch:
    print("Building auto-patch binary...", end=" ", flush=True)
    os.chdir("../autopatch/")
    os.system("go mod tidy")
    os.system("go build -ldflags=\"-H=windowsgui\" -o autovencordpatch.exe")
    os.system("taskkill /f /im autovencordpatch.exe >NUL 2>&1")
    if os.path.exists(f"C:/Users/{getpass.getuser()}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/autovencordpatch.exe"):
        os.remove(f"C:/Users/{getpass.getuser()}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/autovencordpatch.exe")
    os.rename("autovencordpatch.exe", f"C:/Users/{getpass.getuser()}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/autovencordpatch.exe")
    print("done")

os.chdir("../")
print("Cleaning up...", end=" ", flush=True)
os.remove("./installer/cli.go")
if use_autopatch:
    os.remove("./autopatch/autovencordpatch.go")
print("done")

input("\nSuccessfully installed BetterVencordPatch! ")