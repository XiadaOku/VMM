import os
from shutil import move, rmtree
from subprocess import Popen
from sys import platform
from time import sleep

sleep(5)

files = os.listdir(os.getcwd()+"/VMM")
for i in range(len(files)):
    if files[i].lower() == "update" or files[i].lower() == "update.exe":
        continue
    else:
        move(os.getcwd()+"/VMM/"+files[i], os.getcwd()+"/"+files[i])
rmtree(os.getcwd()+"/VMM")

if platform == 'win32':
    os.startfile(os.getcwd()+"/Vangers Mod Manager.exe")
else:
    Popen(["xdg-open", os.getcwd()+"/Vangers Mod Manager"])