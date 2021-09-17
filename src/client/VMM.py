import os
import shutil
import sys
import zipfile
import ctypes
import webbrowser

from ast import literal_eval
from subprocess import Popen
from requests import get
from wget import download

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from interface import Ui_WizardPage


class VMM(QWizardPage, Ui_WizardPage):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        if "save.txt" in os.listdir(os.getcwd()):
            lineCount = 0

            file = open('save.txt')
            for line in file:
                if lineCount == 0:
                    if "Lang_ru" in line:
                        self.lang = "ru"
                    else:
                        self.lang = "en"
                else:
                    self.mods_array = literal_eval(line)
                lineCount += 1
            file.close()
        elif "save" in os.listdir(os.getcwd()):
            lineCount = 0

            file = open('save')
            for line in file:
                if lineCount == 0:
                    self.lang = line.replace("\n", "")
                else:
                    self.mods_array = literal_eval(line)
                lineCount += 1
            file.close()
        else:
            self.mods_array = []
            self.lang = "ru"

        self.langArray = ["ru", "en"]
        self.langIndex = self.langArray.index(self.lang)
        self.vmm_version = "1.1.0-alpha"
        self.release = int(open("release").read())


        self.frame_delFolder.hide()
        self.frame_paramsTransition.hide()

        self.nameToModID = {}
        self.refresh()

        # создание профилей для всех модов при отсутствии сейва (спасибо кэп)
        if "save.txt" not in os.listdir(os.getcwd()) and "save" not in os.listdir(os.getcwd()):
            for mod in self.response:
                self.mods_array.append({"name": self.response[mod]["name"], "vangersPath": pathToVangers,
                                        "mod": mod, "installPath": "", "modVersion": -1})
            self.save()
        else:
            # поддержка вммного "стандарта" сейвов
            for id in range(len(self.mods_array)):
                Imods_array = {"name": "Mod", "vangersPath": pathToVangers, "mod": "none",
                               "installPath": "", "modVersion": -1}
                for key in self.mods_array[id].keys():
                    try:
                        Imods_array[key] = self.mods_array[id][key]
                    except:
                        pass
                self.mods_array[id] = Imods_array

            self.save()

        for mod in self.mods_array:
            profile = QListWidgetItem(mod["name"])
            profile.setTextAlignment(0)
            profile.setBackground(QColor("#A6A6A6"))
            self.list_profiles.addItem(profile)

        self.langIndexCheck = -1
        self.setLanguage()


        self.button_language.clicked.connect(self.setLanguage)
        self.button_refresh.clicked.connect(self.refresh)
        self.button_createProfile.clicked.connect(self.createProfile)
        self.button_delete.clicked.connect(self.deleteProfile)
        self.button_yesDel.clicked.connect(self.delete_folder)
        self.button_noDel.clicked.connect(self.save_folder)
        self.button_cancelDel.clicked.connect(self.cancel_delete)
        self.button_description.clicked.connect(self.description)
        self.button_install.clicked.connect(self.install)
        self.button_play.clicked.connect(self.play)
        self.button_params.clicked.connect(self.params)
        self.button_paramsOK.clicked.connect(self.paramsOk)
        self.list_profiles.itemClicked.connect(self.profileClicked)
        self.edit_profileName.textEdited.connect(self.nameEdited)
        self.pathButton_game.clicked.connect(self.pathGame)
        self.pathButton_install.clicked.connect(self.pathInstall)
        self.button_openFolder.clicked.connect(self.openFolder)



    def errMsg(self, msg):
        self.errorMessage.setText('Error: ' + str(msg))
        self.errorMessage.exec()
        if self.errorMessage.clickedButton():
            sys.exit(0)

    def save(self):
        if "save.txt" in os.listdir(os.getcwd()):
            os.remove(os.getcwd()+"/save.txt")

        file = open('save', 'w')
        file.write(self.lang + "\n")
        file.write(str(self.mods_array))
        file.close()


    def setLanguage(self):
        if self.langIndex == self.langIndexCheck:
            self.langIndex = (self.langIndex + 1) % len(self.langArray)

        self.lang = self.langArray[self.langIndex]

        if self.lang == "en":
            self.modDescription.setWindowTitle("Mod description")

            self.txt_pathGame.setText("Vangers folder path:")
            self.txt_comboMod.setText("Mod:")
            self.txt_pathInstall.setText("Installation path:")
            self.txt_delFolder.setText("Delete mod folder?")
            self.txt_copyTo.setText("Copy to:")

            self.button_createProfile.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                                    "background-image: url(:/buttons/CreateProfile.png);")
            if "Install" in self.button_install.styleSheet():
                self.button_install.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                                  "background-image: url(:/buttons/Install.png);")
            else:
                self.button_install.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                                  "background-image: url(:/buttons/UpdateMod.png);")
            self.button_delete.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                             "background-image: url(:/buttons/Delete.png);")
            self.button_refresh.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                              "background-image: url(:/buttons/Refresh.png);")
            self.button_language.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                               "background-image: url(:/buttons/Lang.png);")
            self.button_yesDel.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                             "background-image: url(:/buttons/Yes.png);")
            self.button_noDel.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                            "background-image: url(:/buttons/No.png);")
            self.button_params.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                             "background-image: url(:/buttons/Parameters.png);")
            self.button_cancelDel.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                                "background-image: url(:/buttons/Cancel.png);")
            self.button_play.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                           "background-image: url(:/buttons/Play.png);")
            self.button_openFolder.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                                 "background-image: url(:/buttons/OpenFolder.png);")

            self.check_paramsOptions.setText("Options")
            self.check_paramsControls.setText("Controls")

        else:
            self.modDescription.setWindowTitle("Описание мода")

            self.txt_pathGame.setText("Путь к папке Вангеров:")
            self.txt_comboMod.setText("Мод:")
            self.txt_pathInstall.setText("Путь установки:")
            self.txt_delFolder.setText("Удалить папку мода?")
            self.txt_copyTo.setText("Копировать в:")

            self.button_createProfile.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                                    "background-image: url(:/buttons/CreateProfile_ru.png);")
            if "Install" in self.button_install.styleSheet():
                self.button_install.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                                  "background-image: url(:/buttons/Install_ru.png);")
            else:
                self.button_install.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                                  "background-image: url(:/buttons/UpdateMod_ru.png);")
            self.button_delete.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                             "background-image: url(:/buttons/Delete_ru.png);")
            self.button_refresh.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                              "background-image: url(:/buttons/Refresh_ru.png);")
            self.button_language.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                               "background-image: url(:/buttons/Lang_ru.png);")
            self.button_params.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                             "background-image: url(:/buttons/Parameters_ru.png);")
            self.button_yesDel.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                             "background-image: url(:/buttons/Yes_ru.png);")
            self.button_noDel.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                            "background-image: url(:/buttons/No_ru.png);")
            self.button_cancelDel.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                                "background-image: url(:/buttons/Cancel_ru.png);")
            self.button_play.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                           "background-image: url(:/buttons/Play_ru.png);")
            self.button_openFolder.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                                 "background-image: url(:/buttons/OpenFolder_ru.png);")

            self.check_paramsOptions.setText("Параметры")
            self.check_paramsControls.setText("Управление")

        self.langIndexCheck = self.langIndex
        self.save()

    def refresh(self):
        try:
            vmm_response = get("https://api.github.com/repos/XiadaOku/VMM/releases").json()[0]
        except Exception as msg:
            self.errMsg(msg)

        if self.vmm_version != vmm_response["tag_name"]:
            text = vmm_response["body"].split("\r\n")
            try:
                ind = text.index(f"[{self.lang}]")
            except:
                ind = text.index("[ru]")

            description = ""
            for line in range(ind + 1, len(text)):
                if len(text[line]) >= 2 and text[line][0] == "[" and text[line][-1] == "]":
                    break
                description += text[line] + "\n"

            if self.lang == "ru":
                self.vmmUpdate.setWindowTitle("Обновление VMM")
                self.vmmUpdate.setText("Доступна новая версия VMM: " + vmm_response["tag_name"] + "\n" +
                                       description + "\nТекущая версия: " + self.vmm_version)
                self.button_update.setText("Обновить")
                self.button_later.setText("Напомнить позже")
            else:
                self.vmmUpdate.setWindowTitle("VMM update")
                self.vmmUpdate.setText("A new VMM version is available: " + vmm_response["tag_name"] + "\n" +
                                       description + "\nCurrent version: " + self.vmm_version)
                self.button_update.setText("Update")
                self.button_later.setText("Remind me later")
            self.vmmUpdate.exec()

            if self.vmmUpdate.clickedButton() == self.button_update:
                try:
                    file = download(vmm_response["assets"][0]["browser_download_url"], os.getcwd())
                except Exception as msg:
                    self.errMsg(msg)

                zip = zipfile.ZipFile(file)
                try:
                    zip.extractall(os.getcwd())
                except Exception as msg:
                    self.errMsg(msg)
                zip.close()
                os.remove(file)

                if self.release:
                    if sys.platform == "win32":
                        os.system("start python src/update.py")
                    elif sys.platform == "linux2":
                        pid = os.fork()
                        if pid == 0:
                            os.system("nohup python3 ./src/update.py &")
                else:
                    if sys.platform == "win32":
                        os.system("start python ../client/update.py")
                    elif sys.platform == "linux2":
                        pid = os.fork()
                        if pid == 0:
                            os.system("nohup python3 ./../client/update.py &")
                sys.exit(0)

        try:
            self.response = get("https://kiv.name/comod").json()
        except Exception as msg:
            self.errMsg(msg)

        # восстановление выбранного мода до обновления списка модов
        mod_id = "none"
        if self.nameToModID:
            mod_id = self.nameToModID[self.combo_mods.currentText()]

        self.combo_mods.clear()
        self.combo_mods.addItem("None")
        self.nameToModID = {"None": "none"}
        for id in self.response:
            self.combo_mods.addItem(self.response[id]["name"])
            self.nameToModID.update({self.response[id]["name"]: id})

        if mod_id == "none":
            self.combo_mods.setCurrentText("None")
        else:
            self.combo_mods.setCurrentText(self.response[mod_id]["name"])

        isOldId = 0
        for id in range(len(self.mods_array)):
            if type(self.mods_array[id]["mod"]) == int:
                if self.mods_array[id]["mod"] == 0:
                    self.mods_array[id]["mod"] = "none"
                else:
                    self.mods_array[id]["mod"] = list(self.response.keys())[self.mods_array[id]["mod"] - 1]
                isOldId = 1
        if isOldId:
            self.save()

    def createProfile(self):
        profile = QListWidgetItem()
        profile.setTextAlignment(0)
        profile.setBackground(QColor("#A6A6A6"))

        if self.lang == "ru":
            self.mods_array.append({"name": "Новый мод", "vangersPath": pathToVangers, "mod": "none",
                                    "installPath": "", "modVersion": -1})
            profile.setText("Новый мод")
        else:
            self.mods_array.append({"name": "New mod", "vangersPath": pathToVangers, "mod": "none",
                                    "installPath": "", "modVersion": -1})
            profile.setText("New mod")
        self.list_profiles.addItem(profile)

        self.save()

    def deleteProfile(self):
        if self.list_profiles.currentItem() and self.list_profiles.currentItem().text() == self.edit_profileName.text():
            if self.mods_array[self.list_profiles.currentRow()]["modVersion"]:
                try:
                    os.listdir(self.mods_array[self.list_profiles.currentRow()]["installPath"] +
                               "/Vangers [" + self.mods_array[self.list_profiles.currentRow()]["name"] + "]")

                    self.frame_delFolder.show()

                    self.list_profiles.setEnabled(0)
                    self.button_createProfile.setEnabled(0)
                    self.frame_profileOptions.setEnabled(0)

                except FileNotFoundError:
                    self.mods_array.pop(self.list_profiles.currentRow())
                    self.list_profiles.takeItem(self.list_profiles.currentRow())

                    self.save()
            else:
                self.mods_array.pop(self.list_profiles.currentRow())
                self.list_profiles.takeItem(self.list_profiles.currentRow())

                self.save()

    def delete_folder(self):
        shutil.rmtree(self.mods_array[self.list_profiles.currentRow()]["installPath"] +
                      "/Vangers [" + self.mods_array[self.list_profiles.currentRow()]["name"] + "]")
        self.mods_array.pop(self.list_profiles.currentRow())
        self.list_profiles.takeItem(self.list_profiles.currentRow())

        self.frame_delFolder.hide()
        self.list_profiles.setEnabled(1)
        self.button_createProfile.setEnabled(1)
        self.frame_profileOptions.setEnabled(1)

        self.save()

    # "оставление". отлично же
    def save_folder(self):
        self.mods_array.pop(self.list_profiles.currentRow())
        self.list_profiles.takeItem(self.list_profiles.currentRow())

        self.frame_delFolder.hide()
        self.list_profiles.setEnabled(1)
        self.button_createProfile.setEnabled(1)
        self.frame_profileOptions.setEnabled(1)

        self.save()

    def cancel_delete(self):
        self.frame_delFolder.hide()
        self.list_profiles.setEnabled(1)
        self.button_createProfile.setEnabled(1)
        self.frame_profileOptions.setEnabled(1)

    def description(self):
        mod_id = self.nameToModID[self.combo_mods.currentText()]
        if self.lang == "ru":
            if mod_id == "none":
                description = "Оригинальные Вангеры без модов"
            else:
                if self.response[mod_id]["site"]:
                    link_button = self.modDescription.addButton("Веб-страница", QMessageBox.ActionRole)

                description = "[" + self.response[mod_id]["name"] + "]\n\n" + \
                              self.response[mod_id]["description"] + "\n\n" + \
                              "Авторы: " + ", ".join(self.response[mod_id]["author"]) + "\n\n"

                if self.response[mod_id]["contacts"]:
                    description += "Контакты: " + ", ".join(self.response[mod_id]["contacts"]) + "\n\n"

                description += "Версия: " + self.response[mod_id]["version"]
        else:
            if mod_id == "none":
                description = "Original Vangers without mods"
            else:
                if self.response[mod_id]["site"]:
                    link_button = self.modDescription.addButton("Web page", QMessageBox.ActionRole)

                if self.response[mod_id]["name_en"]:
                    description = "[" + self.response[mod_id]["name_en"] + "]\n\n"
                else:
                    description = "[" + self.response[mod_id]["name"] + "]\n\n"

                if self.response[mod_id]["description_en"]:
                    description += self.response[mod_id]["description_en"] + "\n\n"
                else:
                    description += self.response[mod_id]["description"] + "\n\n"

                description += "Authors: " + ", ".join(self.response[mod_id]["author"]) + "\n\n"

                if self.response[mod_id]["contacts"]:
                    description += "Contacts: " + ", ".join(self.response[mod_id]["contacts"]) + "\n\n"

                description += "Version: " + self.response[mod_id]["version"]

        self.modDescription.setText(description)

        self.modDescription.exec()

        if mod_id != "none" and self.response[mod_id]["site"] and self.modDescription.clickedButton() == link_button:
            webbrowser.open(self.response[mod_id]["site"])

        if mod_id != "none" and self.response[mod_id]["site"]:
            self.modDescription.removeButton(link_button)

    def install(self):
        if self.list_profiles.currentItem() and self.list_profiles.currentItem().text() == self.edit_profileName.text():
            if self.edit_pathGame.text() and self.edit_pathInstall.text():
                try:
                    os.listdir(self.edit_pathInstall.text())
                except FileNotFoundError:
                    os.makedirs(self.edit_pathInstall.text())

                if "Vangers [" + self.edit_profileName.text() + "]" in os.listdir(self.edit_pathInstall.text()):
                    shutil.rmtree(self.edit_pathInstall.text() + "/Vangers [" + self.edit_profileName.text() + "]")

                shutil.copytree(self.edit_pathGame.text(), self.edit_pathInstall.text() + "/Vangers [" +
                                self.edit_profileName.text() + "]")

                if self.nameToModID[self.combo_mods.currentText()] != "none":
                    try:
                        self.response = get("https://kiv.name/comod").json()
                        mod_id = self.nameToModID[self.combo_mods.currentText()]

                        file = download("https://kiv.name/comod/" + mod_id + "/get", self.edit_pathInstall.text() +
                                        "/Vangers [" + self.edit_profileName.text() + "]")
                    except Exception as msg:
                        self.errMsg(msg)

                    zip = zipfile.ZipFile(file)
                    try:
                        zip.extractall(self.edit_pathInstall.text() + "/Vangers [" + self.edit_profileName.text() + "]")
                    except Exception as msg:
                        self.errMsg(msg)
                    zip.close()
                    os.remove(file)

                    self.combo_bat.clear()
                    self.launchFileNames = {"Windows 32bit (русский)": "Win32_ru.bat",
                                            "Windows 64bit (русский)": "Win64_ru.bat",
                                            "Windows 32bit (english)": "Win32_en.bat",
                                            "Windows 64bit (english)": "Win64_en.bat",
                                            "Linux (русский)": "Linux_ru.sh",
                                            "Linux (english)": "Linux_en.sh"}

                    for bat in range(len(self.response[mod_id]["launch"])):
                        lresponse = self.response[mod_id]["launch"]
                        if list(lresponse.keys())[bat] not in ["mac_ru", "mac_en"]:
                            if not lresponse[list(lresponse.keys())[bat]]:
                                file = open(self.edit_pathInstall.text() + "/Vangers [" + self.edit_profileName.text() +
                                            "]/" + list(launchFiles.keys())[bat], "w")
                                file.write(launchFiles[list(launchFiles.keys())[bat]])
                                file.close()
                            else:
                                self.launchFileNames[list(self.launchFileNames.keys())[bat]] = lresponse[
                                    list(lresponse.keys())[bat]]
                            self.combo_bat.addItem(list(self.launchFileNames.keys())[bat])

                else:
                    self.combo_bat.clear()
                    self.launchFileNames = {"Windows 32bit (русский)": "Win32_ru.bat",
                                            "Windows 64bit (русский)": "Win64_ru.bat",
                                            "Windows 32bit (english)": "Win32_en.bat",
                                            "Windows 64bit (english)": "Win64_en.bat",
                                            "Linux (русский)": "Linux_ru.sh",
                                            "Linux (english)": "Linux_en.sh"}

                    for file in range(len(launchFiles)):
                        f = open(self.edit_pathInstall.text() + "/Vangers [" + self.edit_profileName.text() +
                                 "]/" + list(launchFiles.keys())[file], "w")
                        f.write(launchFiles[list(launchFiles.keys())[file]])
                        f.close()

                        self.combo_bat.addItem(list(self.launchFileNames.keys())[file])

                self.mods_array[self.list_profiles.currentRow()]["name"] = self.edit_profileName.text()
                self.mods_array[self.list_profiles.currentRow()]["vangersPath"] = self.edit_pathGame.text()
                self.mods_array[self.list_profiles.currentRow()]["mod"] = self.nameToModID[self.combo_mods.currentText()]
                self.mods_array[self.list_profiles.currentRow()]["installPath"] = self.edit_pathInstall.text()
                if self.nameToModID[self.combo_mods.currentText()] != "none":
                    self.mods_array[self.list_profiles.currentRow()]["modVersion"] = \
                        self.response[self.nameToModID[self.combo_mods.currentText()]]["version"]
                else:
                    self.mods_array[self.list_profiles.currentRow()]["modVersion"] = "1"

                self.save()

            else:
                text = ""

                if not self.edit_pathGame.text():
                    if self.lang == "ru":
                        text += "Путь к папке Вангеров не указан\n"
                    else:
                        text += "Vangers folder path not specified\n"

                if not self.edit_pathInstall.text():
                    if self.lang == "ru":
                        text += "Путь установки не указан"
                    else:
                        text += "Installation path not specified"

                self.infoMessage.setText(text)
                self.infoMessage.exec()

    def play(self):
        if self.list_profiles.currentItem() and self.list_profiles.currentItem().text() == self.edit_profileName.text():
            id = self.list_profiles.currentRow()
            if self.mods_array[id]["modVersion"] != -1 and self.combo_bat.currentText() != "":
                cwd = os.getcwd()
                os.chdir(self.mods_array[id]["installPath"] + "/Vangers [" + self.mods_array[id]["name"] + "]")

                if sys.platform == "win32":
                    os.startfile(self.mods_array[id]["installPath"] + "/Vangers [" + self.mods_array[id]["name"] +
                                 "]/" + self.launchFileNames[self.combo_bat.currentText()])
                elif sys.platform == "linux2":
                    Popen(["xdg-open", self.mods_array[id]["installPath"] + "/Vangers [" + self.mods_array[id]["name"] +
                           "]/" + self.launchFileNames[self.combo_bat.currentText()]])
                os.chdir(cwd)
            else:
                text = ""

                if self.mods_array[id]["modVersion"] == -1:
                    if self.lang == "ru":
                        text += "Мод не установлен\n"
                    else:
                        text += "Mod not installed\n"

                if self.combo_bat.currentText() == "":
                    if self.lang == "ru":
                        text += "Файл запуска не выбран"
                    else:
                        text += "Launch file not chosen"

                self.infoMessage.setText(text)
                self.infoMessage.exec()

    def params(self):
        if self.list_profiles.currentItem() and self.list_profiles.currentItem().text() == self.edit_profileName.text():
            mod_id = self.list_profiles.currentRow()
            if self.mods_array[mod_id]["installPath"]:
                self.check_save00.setEnabled(0)
                self.check_save01.setEnabled(0)
                self.check_save02.setEnabled(0)
                self.check_save03.setEnabled(0)
                self.check_save04.setEnabled(0)
                self.check_save05.setEnabled(0)
                self.check_save06.setEnabled(0)
                self.check_save07.setEnabled(0)
                self.check_save08.setEnabled(0)
                self.button_openFolder.setEnabled(0)
                self.check_paramsOptions.setEnabled(0)
                self.check_paramsControls.setEnabled(0)

                try:
                    options = os.listdir(self.mods_array[mod_id]["installPath"] + "/Vangers [" +
                                         self.mods_array[mod_id]["name"] + "]/data")
                    self.check_paramsOptions.setEnabled("options.dat" in options)
                    self.check_paramsControls.setEnabled("controls.dat" in options)

                    saves = os.listdir(self.mods_array[mod_id]["installPath"] + "/Vangers [" +
                                       self.mods_array[mod_id]["name"] + "]/data/savegame")
                    self.button_openFolder.setEnabled(1)
                    self.check_save00.setEnabled("save00.dat" in saves)
                    self.check_save01.setEnabled("save01.dat" in saves)
                    self.check_save02.setEnabled("save02.dat" in saves)
                    self.check_save03.setEnabled("save03.dat" in saves)
                    self.check_save04.setEnabled("save04.dat" in saves)
                    self.check_save05.setEnabled("save05.dat" in saves)
                    self.check_save06.setEnabled("save06.dat" in saves)
                    self.check_save07.setEnabled("save07.dat" in saves)
                    self.check_save08.setEnabled("save08.dat" in saves)
                except FileNotFoundError:
                    if self.lang == "ru":
                        self.infoMessage.setText("Папка не найдена")
                    else:
                        self.infoMessage.setText("Folder not found")
                    self.infoMessage.exec()
                    return

                self.frame_paramsTransition.show()
                self.list_profiles.setEnabled(0)
                self.button_createProfile.setEnabled(0)

                self.list_paramsProfiles.clear()
                for profile in range(self.list_profiles.count()):
                    new_profile = QListWidgetItem(self.mods_array[profile]["name"])
                    new_profile.setTextAlignment(0)
                    new_profile.setBackground(QColor("#A6A6A6"))

                    self.list_paramsProfiles.addItem(new_profile)
                    self.list_paramsProfiles.item(profile).setHidden(1)

                    if profile == self.list_profiles.currentRow():
                        continue
                    if self.mods_array[profile]["installPath"]:
                        try:
                            os.listdir(self.mods_array[profile]["installPath"] + "/Vangers [" +
                                       self.mods_array[profile]["name"] + "]/data/savegame")
                            self.list_paramsProfiles.item(profile).setHidden(0)
                        except FileNotFoundError:
                            continue

            else:
                if self.lang == "ru":
                    self.infoMessage.setText("Мод не установлен")
                else:
                    self.infoMessage.setText("Mod not installed")
                self.infoMessage.exec()

    def paramsOk(self):
        mod_id = self.list_profiles.currentRow()
        if self.list_paramsProfiles.currentItem():
            checkedParams = []
            if self.check_save00.isChecked():
                checkedParams.append("savegame/save00.dat")
            if self.check_save01.isChecked():
                checkedParams.append("savegame/save01.dat")
            if self.check_save02.isChecked():
                checkedParams.append("savegame/save02.dat")
            if self.check_save03.isChecked():
                checkedParams.append("savegame/save03.dat")
            if self.check_save04.isChecked():
                checkedParams.append("savegame/save04.dat")
            if self.check_save05.isChecked():
                checkedParams.append("savegame/save05.dat")
            if self.check_save06.isChecked():
                checkedParams.append("savegame/save06.dat")
            if self.check_save07.isChecked():
                checkedParams.append("savegame/save07.dat")
            if self.check_save08.isChecked():
                checkedParams.append("savegame/save08.dat")
            if self.check_paramsOptions.isChecked():
                checkedParams.append("options.dat")
            if self.check_paramsControls.isChecked():
                checkedParams.append("controls.dat")

            for checked in checkedParams:
                shutil.copyfile(self.mods_array[mod_id]["installPath"] + "/Vangers [" +
                                self.mods_array[mod_id]["name"] + "]/data/" + checked,
                                self.mods_array[self.list_paramsProfiles.currentRow()]["installPath"] + "/Vangers [" +
                                self.mods_array[self.list_paramsProfiles.currentRow()]["name"] + "]/data/" + checked)

        self.frame_paramsTransition.hide()
        self.list_profiles.setEnabled(1)
        self.button_createProfile.setEnabled(1)

    def profileClicked(self):
        self.list_profiles.currentItem().setText(self.mods_array[self.list_profiles.currentRow()]["name"])
        self.edit_profileName.setText(self.mods_array[self.list_profiles.currentRow()]["name"])
        self.edit_pathGame.setText(self.mods_array[self.list_profiles.currentRow()]["vangersPath"])
        self.edit_pathInstall.setText(self.mods_array[self.list_profiles.currentRow()]["installPath"])
        self.combo_bat.clear()

        if self.mods_array[self.list_profiles.currentRow()]["mod"] == "none":
            self.combo_mods.setCurrentText("None")
        else:
            self.combo_mods.setCurrentText(self.response[self.mods_array[self.list_profiles.currentRow()]["mod"]]["name"])

        self.launchFileNames = {"Windows 32bit (русский)": "Win32_ru.bat", "Windows 64bit (русский)": "Win64_ru.bat",
                                "Windows 32bit (english)": "Win32_en.bat",
                                "Windows 64bit (english)": "Win64_en.bat", "Linux (русский)": "Linux_ru.sh",
                                "Linux (english)": "Linux_en.sh"}

        mod_id = self.list_profiles.currentRow()
        for bat in range(len(self.launchFileNames)):
            if self.mods_array[self.list_profiles.currentRow()]["mod"] != "none":
                lresponse = self.response[self.mods_array[mod_id]["mod"]]["launch"]
                if lresponse[list(lresponse.keys())[bat]]:
                    self.launchFileNames[list(self.launchFileNames.keys())[bat]] = lresponse[list(lresponse.keys())[bat]]
            self.combo_bat.addItem(list(self.launchFileNames.keys())[bat])

        if self.mods_array[self.list_profiles.currentRow()]["mod"] != "none":
            if self.response[self.mods_array[mod_id]["mod"]]["version"] != \
                    self.mods_array[mod_id]["modVersion"] and self.mods_array[mod_id]["modVersion"] != -1:

                if self.lang == "ru":
                    self.button_install.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                                      "background-image: url(:/buttons/UpdateMod_ru.png);")
                else:
                    self.button_install.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                                      "background-image: url(:/buttons/UpdateMod.png);")
            else:

                if self.lang == "ru":
                    self.button_install.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                                      "background-image: url(:/buttons/Install_ru.png);")
                else:
                    self.button_install.setStyleSheet("background-color: rgba(255, 255, 255, 0);"
                                                      "background-image: url(:/buttons/Install.png);")

    def openFolder(self):
        path = self.mods_array[self.list_profiles.currentRow()]["installPath"] + "/Vangers [" + \
               self.mods_array[self.list_profiles.currentRow()]["name"] + "]/data/savegame"
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "linux2":
            Popen(["xdg-open", path])

    def nameEdited(self, text):
        if self.list_profiles.currentItem():
            self.list_profiles.currentItem().setText(text)

    def pathGame(self):
        folder = QFileDialog.getExistingDirectory()
        if folder:
            self.edit_pathGame.setText(folder)

    def pathInstall(self):
        folder = QFileDialog.getExistingDirectory()
        if folder:
            self.edit_pathInstall.setText(folder)



def main():
    # одномониторная недоподдержка high-dpi
    if sys.platform == "win32":
        dpi = ctypes.windll.shcore.GetScaleFactorForDevice(1) / 100
        os.environ["QT_SCREEN_SCALE_FACTORS"] = str(dpi)

    app = QApplication(sys.argv)
    window = VMM()
    window.show()
    app.exec_()


if __name__ == '__main__':
    launchFiles = {"Win32_ru.bat": "@echo off \ncd data \n.\\..\\bin\\windows-32\\vangers.exe -russian",
                   "Win64_ru.bat": "@echo off \ncd data \n.\\..\\bin\\windows-64\\vangers.exe -russian",
                   "Win32_en.bat": "@echo off \ncd data \n.\\..\\bin\\windows-32\\vangers.exe",
                   "Win64_en.bat": "@echo off \ncd data \n.\\..\\bin\\windows-64\\vangers.exe",
                   "Linux_ru.sh": "#!/bin/sh \nBASEDIR=$(pwd) \nexport \n" +
                                  "LD_LIBRARY_PATH=$BASEDIR/bin/linux/lib64:$LD_LIBRARY_PATH \ncd data \n" +
                                  "./../bin/linux/vangers64 -russian",
                   "Linux_en.sh": "#!/bin/sh \nBASEDIR=$(pwd) \nexport \n" +
                                  "LD_LIBRARY_PATH=$BASEDIR/bin/linux/lib64:$LD_LIBRARY_PATH \ncd data \n" +
                                  "./../bin/linux/vangers64"
                   }


    pathToVangers = ""

    # Поиск папки в стиме
    drive = os.getcwd()[:os.getcwd().find("\\")]
    try:
        os.listdir(drive + "/Program Files (x86)/Steam/SteamApps/Common/Vangers")
        pathToVangers = drive + "/Program Files (x86)/Steam/SteamApps/Common/Vangers"
    except:
        pass

    try:
        os.listdir(drive + "/Program Files/Steam/SteamApps/Common/Vangers")
        pathToVangers = drive + "/Program Files/Steam/SteamApps/Common/Vangers"
    except:
        pass

    main()
