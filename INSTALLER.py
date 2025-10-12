import os
import json
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

rel = json.loads(releases.text)
for asset in rel[0]["assets"]:
    if f"VencordInstaller-{"no_" if not openasar else ""}openasar{suffix}" in asset["browser_download_url"]:
        open(f"VencordInstaller{suffix}", "wb").write(requests.get(asset["browser_download_url"]).content)
        input(f"Successfully downloaded Sunshine {rel[0]["name"]}! ")
        break
