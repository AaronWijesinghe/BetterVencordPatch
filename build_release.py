import os
import shutil

os.chdir(os.path.dirname(__file__))
def clear():
    for i in range(2):
        os.system("clear")

def run_sh(sh):
    for cmd in sh.split("\n"):
        os.system(f"{cmd}")

def build(openasar, op):
    global branch
    global send_success_notifications

    suffix = ".app" if op == "Darwin" else ".exe"
    branch = "stable"
    send_success_notifications = True

    cli_code = open("./files/cli.go", "r").read()
    cli_code = cli_code.replace("var pyOpenAsar = false", f"var pyOpenAsar = {str(openasar).lower()}")
    cli_code = cli_code.replace("var pyBranch = \"stable\"", f"var pyBranch = \"{branch}\"")
    cli_code = cli_code.replace("var pySendSuccessNotifications = true", f"var pySendSuccessNotifications = {str(send_success_notifications).lower()}")
    open("./installer/cli.go", "w").write(cli_code)

    os.chdir("./installer/")
    build_vi = f"""
    go mod tidy
    CGO_ENABLED=0{" GOOS=windows GOARCH=amd64 " if op == "Windows" else " "}go build{" -ldflags=\"-H=windowsgui\" " if op == "Windows" else " "}--tags cli
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
    os.system(f"mv VencordInstaller{suffix} ../VencordInstaller{suffix}")

    os.chdir("../")
    os.remove("./installer/cli.go")
    os.system(f"mv VencordInstaller{suffix} ./binaries/VencordInstaller-{"no_" if not openasar else ""}openasar{suffix}")

clear()
if os.path.exists("./binaries/"):
    shutil.rmtree("./binaries")
os.mkdir("./binaries/")

os.system("cp ./files/autovencordpatch.go ./autopatch/autovencordpatch.go")
os.system("cp ./files/autovencordpatch_win.go ./autopatch/autovencordpatch_win.go")
os.chdir("./autopatch")
build_avp = f"""
go mod tidy
CGO_ENABLED=0 go build -o autovencordpatch autovencordpatch.go
CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build -ldflags=\"-H=windowsgui\" -o autovencordpatch.exe autovencordpatch_win.go
"""
run_sh(build_avp)
os.chdir("../")
os.rename("./autopatch/autovencordpatch", "./binaries/autovencordpatch")
os.rename("./autopatch/autovencordpatch.exe", "./binaries/autovencordpatch.exe")
os.remove("./autopatch/autovencordpatch.go")
os.remove("./autopatch/autovencordpatch_win.go")

for op in ["Windows", "Darwin"]:
    for openasar in [False, True]:
        build(openasar, op)
os.system("cp ./autopatch/org.aaron.autovencordpatch.plist ./binaries/org.aaron.autovencordpatch.plist")