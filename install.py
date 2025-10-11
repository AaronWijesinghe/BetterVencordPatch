import os

os.chdir(os.path.dirname(__file__))
def clear():
    for i in range(2):
        os.system("clear")

def run_sh(sh):
    for cmd in sh.split("\n"):
        os.system(f"{cmd}")

clear()
print("[AutoVencordPatch Installer]")
branch = input("Enter the branch of Discord to be automatically patched (stable, ptb, canary): ")
openasar = input("Automatically patch OpenAsar (y/n)? ").lower().strip() == "y"
if branch not in ["stable", "ptb", "canary"]:
    input("This version of Discord doesn't exist. ")
    exit()

discords = {
    "stable": "Discord.app",
    "ptb": "Discord PTB.app",
    "canary": "Discord Canary.app"
}
clear()
print("[Installing AutoVencordPatch]")
print("Preparing install environment...", end=" ", flush=True)
avp_code = open("./files/autovencordpatch.go", "r").read()
avp_code = avp_code.replace("Discord.app", discords[branch])
open("./autovencordpatch/autovencordpatch.go", "w").write(avp_code)
cli_code = open("./files/cli.go", "r").read()
cli_code = cli_code.replace("var pyOpenAsar = false", f"var pyOpenAsar = {str(openasar).lower()}")
cli_code = cli_code.replace("var pyBranch = \"stable\"", f"var pyBranch = \"{branch}\"")
open("./installer/cli.go", "w").write(cli_code)
print("done")

os.chdir("./installer/")
build_vi = """
go mod tidy
CGO_ENABLED=0 go build --tags cli
mkdir -p VencordInstaller.app/Contents/MacOS
mkdir -p VencordInstaller.app/Contents/Resources
cp macos/Info.plist VencordInstaller.app/Contents/Info.plist
mv VencordInstaller VencordInstaller.app/Contents/MacOS/VencordInstaller
cp macos/icon.icns VencordInstaller.app/Contents/Resources/icon.icns
rm -rf ../VencordInstaller.app
mv VencordInstaller.app ../VencordInstaller.app
"""
print("Building VencordInstaller.app...", end=" ", flush=True)
run_sh(build_vi)
print("done")

os.chdir("../autovencordpatch/")
build_avp = """
go get github.com/fsnotify/fsnotify
CGO_ENABLED=0 go build -o autovencordpatch autovencordpatch.go
chmod +x autovencordpatch
mv autovencordpatch ../VencordInstaller.app/Contents/Resources/autovencordpatch
"""
print("Building AutoVencordPatch...", end=" ", flush=True)
run_sh(build_avp)
print("done")

os.chdir("../")
install = """
cp autovencordpatch/org.aaron.autovencordpatch.plist ~/Library/LaunchAgents/org.aaron.autovencordpatch.plist
rm -rf /Applications/VencordInstaller.app
mv VencordInstaller.app /Applications/VencordInstaller.app
launchctl unload ~/Library/LaunchAgents/org.aaron.autovencordpatch.plist > /dev/null 2>&1
launchctl load ~/Library/LaunchAgents/org.aaron.autovencordpatch.plist > /dev/null 2>&1
open /Applications/VencordInstaller.app
"""
print("Running install scripts...", end=" ", flush=True)
run_sh(install)
print("done")

print("Cleaning up...", end=" ", flush=True)
os.remove("./installer/cli.go")
os.remove("./autovencordpatch/autovencordpatch.go")
print("done")

input("\nSuccessfully installed AutoVencordPatch! ")