import os

from shutil import move, rmtree
from time import sleep


# чтобы вмм успел закрыться
sleep(5)

files = os.listdir(os.getcwd()+"/VMM")
for file in files:
    if file == "src":
        continue
    else:
        move(os.getcwd()+"/VMM/"+file, os.getcwd()+"/"+file)

files = os.listdir(os.getcwd()+"/VMM/src")
for file in files:
    if file == "update.py":
        continue
    else:
        move(os.getcwd()+"/VMM/src/"+file, os.getcwd()+"/src/"+file)

rmtree(os.getcwd()+"/VMM")

os.system("python launcher.py")
