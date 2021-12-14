# VMM #

All source code is published under the GPLv3 license.

You'll need resources of Vangers to install mods on them.

## Dependencies ##

* Python3 >= 3.8.10
* pip
* wget
* requests
* PyQt5

* pyinstaller (build for launcher.exe)

## Resources ##

Use pyuic5 to build interface and pyrcc5 to build resources

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
	
	themes
		classic_ru
			resource_rc.py
			theme.json
			language.json
		classic_en
			same as classic_ru
		dark
			same as classic_ru except it's without language.json (read theme.json)
	
	languages
		ru.json
		en.json