import os
import shutil

os.chdir(os.path.dirname(__file__))
def clear():
    print("\033[2J\033[3J\033[H", end='')

def run_sh(sh):
    for cmd in sh.split("\n"):
        os.system(f"{cmd}")

def build(openasar, op):
    global branch
    global send_success_notifications

    suffix = ".app" if op == "Darwin" else ".exe"
    branch = "stable"
    send_success_notifications = True

    build_vi = f"""
    go mod tidy
    CGO_ENABLED=0{" GOOS=windows GOARCH=amd64 " if op == "Windows" else " "}go build -ldflags=\"{"-H=windowsgui " if op == "Windows" else ""}-X main.branch={branch} -X main.patchOpenAsar={str(openasar).lower()} -X main.sendSuccessNotifications={str(send_success_notifications).lower()}\" --tags cli
    """
    build_vi_darwin = """
    mkdir -p VencordInstaller.app/Contents/MacOS
    mkdir -p VencordInstaller.app/Contents/Resources
    cp macos/Info.plist VencordInstaller.app/Contents/Info.plist
    mv VencordInstaller VencordInstaller.app/Contents/MacOS/VencordInstaller
    cp macos/icon.icns VencordInstaller.app/Contents/Resources/icon.icns
    rm -rf ../VencordInstaller.app
    """
    run_sh(build_vi)
    if op == "Darwin":
        run_sh(build_vi_darwin)
    os.system(f"mv VencordInstaller{suffix} ../binaries/VencordInstaller-{"no_" if not openasar else ""}openasar{suffix}")

def build_installer():
    build_installer_win = f"""
    wine $HOME/.wine/drive_c/Python314/python.exe -m pip install -r requirements.txt --upgrade
    wine $HOME/.wine/drive_c/Python314/Scripts/pyinstaller.exe INSTALLER.py --onefile
    mv ./dist/INSTALLER.exe ./binaries/INSTALLER.exe
    rm -rf ./build/ ./dist/ INSTALLER.spec
    """

    build_installer_darwin = f"""
    pip3 install -r requirements.txt --upgrade
    pyinstaller INSTALLER.py --onefile
    mv ./dist/INSTALLER ./binaries/INSTALLER
    rm -rf ./build/ ./dist/ INSTALLER.spec
    """

    run_sh(build_installer_win)
    run_sh(build_installer_darwin)

clear()
if os.path.exists("./binaries/"):
    shutil.rmtree("./binaries/")
os.mkdir("./binaries/")

build_installer()

os.chdir("./installer/")
build_avp = f"""
go mod tidy
CGO_ENABLED=0 go build -o autovencordpatch --tags avp_macos
CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build -ldflags=\"-H=windowsgui\" -o autovencordpatch.exe --tags avp_win
"""
run_sh(build_avp)
os.rename("./autovencordpatch", "../binaries/autovencordpatch")
os.rename("./autovencordpatch.exe", "../binaries/autovencordpatch.exe")

for op in ["Windows", "Darwin"]:
    for openasar in [False, True]:
        build(openasar, op)
os.system("cp ../autopatch/org.aaron.autovencordpatch.plist ../binaries/org.aaron.autovencordpatch.plist")