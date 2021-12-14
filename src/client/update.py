import os
import sys

from shutil import move, rmtree
from time import sleep


# чтобы вмм успел закрыться... надо переделать
sleep(5)

files = os.listdir(os.getcwd()+"/VMM")
for file in files:
    if file in ["src", "themes", "languages"]:
        continue
    else:
        move(os.getcwd()+"/VMM/"+file, os.getcwd()+"/"+file)

files = os.listdir(os.getcwd()+"/VMM/src")
for file in files:
    if file == "update.py":
        continue
    else:
        move(os.getcwd()+"/VMM/src/"+file, os.getcwd()+"/src/"+file)

files = os.listdir(os.getcwd() + "/VMM/themes")
for file in files:
    move(os.getcwd() + "/VMM/themes/" + file, os.getcwd() + "/themes/" + file)

files = os.listdir(os.getcwd() + "/VMM/languages")
for file in files:
    move(os.getcwd() + "/VMM/languages/" + file, os.getcwd() + "/languages/" + file)


rmtree(os.getcwd()+"/VMM")

if sys.platform == "win32":
    os.system("start python launcher.py")
elif sys.platform == "linux":
    pid = os.fork()
    if pid == 0:
        os.system("nohup python3 ./launcher.py &")
