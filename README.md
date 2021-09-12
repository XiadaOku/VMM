# VMM #

All source code is published under the GPLv3 license.

You'll need resources of Vangers to install mods on them.

## Dependencies ##

* PyQt5
* wget
* requests
* pyinstaller (build)

## Resources ##

Resources are given as pack of pictures, qrc and ui files.

You can build them with pyrcc5 and pyuic5 from PyQt.

interface.py doesn't match with pyuic5 .py file so remember to write additional code when changing interface

## Build ##

You can build VMM and update using pyinstaller \*.spec.

Full set of components: VMM, update, .ico, .ttf.
