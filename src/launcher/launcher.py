import vmm_release

import sys
import os
import platform
import ssl
import json

from wget import download
from subprocess import PIPE, Popen, check_output


def version(ver):
    return tuple(map(int, (ver.split("."))))

def install_python():
    if sys.platform == "win32":
        print("downloading python")

        if platform.machine().endswith('64'):
            python_installer = "python-3.8.10-amd64.exe"
        else:
            python_installer = "python-3.8.10.exe"
        file = download(f"https://www.python.org/ftp/python/3.8.10/{python_installer}", os.getcwd())

        print("\ninstalling python:", python_installer)
        try:
            check_output([python_installer, "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0"])
        except:
            pass
        print("install complete")

        os.remove(file)
        print("installer removed")

    else:
        print("please install Python3 >= 3.8.10 by yourself: https://www.python.org/downloads/release/python-3810/")


ssl._create_default_https_context = ssl._create_unverified_context

p = Popen("python --version", shell=True, stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()
if stderr != b'':
    install_python()
else:
    python_version = version(str(stdout, "utf-8")[7:-2])
    if python_version < version("3.8.10"):
        print("python version:", python_version)
        install_python()
    else:
        print("python version: OK!")


print("upgrading pip")
check_output(["python", "-m", "pip", "install", "--upgrade", "pip"])
print("done")

required = open("../requirements.txt").read().split("\n")
installed = json.loads(str(check_output(["python", "-m", "pip", "list", "--format", "json"]), "utf-8"))
missing = set(required) - set(installed[i]["name"] for i in range(len(installed)))

if missing:
    check_output(["python", '-m', 'pip', 'install', *missing])
else:
    print("no packages to install")

if vmm_release.release:
    os.system("python src/VMM.py")
else:
    os.system("python ../client/VMM.py")
