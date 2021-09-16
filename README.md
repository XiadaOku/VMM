# VMM #

All source code is published under the GPLv3 license.

You'll need resources of Vangers to install mods on them.

## Dependencies ##

* Python3 >= 3.8.10
* PyQt5
* wget
* requests
* pyinstaller (build)

## Resources ##

Resources are given as pack of pictures, qrc and ui files.

You can build them with pyrcc5 and pyuic5 from PyQt.

interface.py doesn't match with pyuic5 .py file so remember to write additional code when changing interface

## Build ##

If you need to build launcher you can use "pyinstaller launcher.spec"

In release you can set is it release or not. This will change some paths so if release is true you must do V this V thing 

Release files:
	
	launcher.py
	launcher.exe
	launch.sh
	requirements.txt
	release
	vmm.ico
	Vangers.ttf

	src
		VMM.py
		interface.py
		resource_rc.py
		update.py
