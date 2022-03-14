import os
import shutil
import sys
import zipfile
import ctypes
import webbrowser
import json

from requests import get
from wget import download

from PyQt5 import QtGui, QtWidgets

from interface import Ui_WizardPage

vmm_version = "1.3.1"


class VMM(QtWidgets.QWizardPage, Ui_WizardPage):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.frame_vmmSettings.hide()
        self.frame_delFolder.hide()
        self.frame_paramsTransition.hide()

        self.txt_version.setText(vmm_version)

        self.release = int(open("release").read())

        if self.release:
            self.themePath = "themes"
            self.languagePath = "languages"
        else:
            self.themePath = "../themes"
            self.languagePath = "../languages"

        self.nameToModID = {}
        self.currentUpdate = False
        self.last_theme = None

        if "save" in os.listdir(os.getcwd()):
            file = open('save', encoding="utf8")

            if file.readline()[:-1] == "en":
                self.theme = "classic_en"
                self.language = ""
            else:
                self.theme = "classic_ru"
                self.language = ""
            self.mods_array = json.loads(file.read().replace("\'", "\""))

            file.close()
        elif "save.json" in os.listdir(os.getcwd()):
            file = open("save.json", encoding="utf8")

            self.mods_array = json.loads(file.read())
            self.theme = self.mods_array[0]
            self.language = self.mods_array[1]
            self.mods_array = self.mods_array[2]

            file.close()
        else:
            self.mods_array = []
            self.theme = "classic_ru"
            self.language = ""


        # создание профилей для всех модов при отсутствии сейва (спасибо кэп)
        if "save.json" not in os.listdir(os.getcwd()) and "save" not in os.listdir(os.getcwd()):
            try:
                response = get("https://kiv.name/comod").json()
            except Exception as msg:
                self.errMsg(msg)

            for mod in response:
                self.mods_array.append({"name": response[mod]["name"]["ru"], "vangersPath": pathToVangers,
                                        "mod": mod, "installPath": "", "modVersion": -1})
            del response
        else:
            # поддержка вммного "стандарта" сейвов
            for id in range(len(self.mods_array)):
                Imods_array = {"name": "Mod", "vangersPath": pathToVangers, "mod": "none",
                               "installPath": "", "modVersion": -1}
                for key in self.mods_array[id].keys():
                    if key in Imods_array.keys():
                        Imods_array[key] = self.mods_array[id][key]

                self.mods_array[id] = Imods_array.copy()
        self.save()

        self.inner_mods_array = []
        for elem in self.mods_array:
            self.inner_mods_array.append(elem.copy())

        self.setTheme(self.theme)
        self.setLanguage([f"{self.languagePath}/{self.language}.json", f"{self.themePath}{self.theme}/language.json"][self.theme_config["constLanguage"]])

        for mod in self.mods_array:
            profile = QtWidgets.QListWidgetItem(mod["name"])
            profile.setTextAlignment(0)
            profile.setBackground(QtGui.QColor(self.theme_config["listelem"]["profiles"]["background"]))
            profile.setForeground(QtGui.QColor(self.theme_config["listelem"]["profiles"]["text"]))

            self.list_profiles.addItem(profile)

        self.refresh()


        self.button_vmmSettings.clicked.connect(self.vmmSettingsOpen)
        self.button_vmmSettingsOK.clicked.connect(self.vmmSettingsOK)
        self.combo_themes.currentIndexChanged.connect(self.themeSelected)

        self.button_delete.clicked.connect(self.deleteProfile)
        self.button_yesDel.clicked.connect(self.delete_folder)
        self.button_noDel.clicked.connect(self.save_folder)
        self.button_cancelDel.clicked.connect(self.cancel_delete)

        self.button_refresh.clicked.connect(self.refresh)

        self.button_description.clicked.connect(self.description)
        self.button_install.clicked.connect(self.install)
        self.button_play.clicked.connect(self.play)

        self.button_params.clicked.connect(self.params)
        self.button_paramsOK.clicked.connect(self.paramsOK)
        self.button_openFolder.clicked.connect(self.openFolder)

        self.button_createProfile.clicked.connect(self.createProfile)
        self.list_profiles.itemClicked.connect(self.profileClicked)
        self.edit_profileName.textEdited.connect(self.nameEdited)

        self.pathButton_game.clicked.connect(self.pathGame)
        self.pathButton_install.clicked.connect(self.pathInstall)

        self.edit_pathGame.textEdited.connect(self.pathGameChanged)
        self.edit_pathInstall.textEdited.connect(self.pathInstallChanged)
        self.combo_mods.currentTextChanged.connect(self.comboModsChanged)



    def errMsg(self, msg):
        self.errorMessage.setText('Error: ' + str(msg))
        self.errorMessage.exec()
        if self.errorMessage.clickedButton():
            sys.exit(0)

    def save(self):
        if "save" in os.listdir(os.getcwd()):
            os.remove(os.getcwd()+"/save")

        file = open("save.json", "w", encoding="utf8")
        file.write(json.dumps([self.theme, self.language, self.mods_array], indent=4))
        file.close()


    def vmmSettingsOpen(self):
        self.frame_vmmSettings.show()
        self.list_profiles.setEnabled(0)
        self.button_createProfile.setEnabled(0)
        self.frame_profileOptions.setEnabled(0)

        self.combo_languages.setEnabled(1)

        self.combo_themes.clear()
        for elem in os.listdir(self.themePath):
            if os.path.isdir(f"{self.themePath}/{elem}"):
                self.combo_themes.addItem(elem)
        self.combo_themes.setCurrentText(self.theme)

        self.combo_languages.clear()
        for elem in os.listdir(self.languagePath):
            if elem[-5:] == ".json":
                self.combo_languages.addItem(elem)
        self.combo_languages.setCurrentText(f"{self.language}.json")

    def themeSelected(self):
        if len(os.listdir(self.themePath)) != 0:
            if self.combo_themes.currentText() in os.listdir(self.themePath):
                file = open(f"{self.themePath}/{self.combo_themes.currentText()}/theme.json", encoding="utf-8")
                isConst = json.loads(file.read())["constLanguage"]
                file.close()

                self.combo_languages.clear()
                if isConst:
                    self.combo_languages.setEnabled(0)
                else:
                    self.combo_languages.setEnabled(1)
                    for elem in os.listdir(self.languagePath):
                        if elem[-5:] == ".json":
                            self.combo_languages.addItem(elem)
            elif self.combo_themes.currentText() != "":
                self.combo_themes.clear()
                for elem in os.listdir(self.themePath):
                    if os.path.isdir(f"{self.themePath}/{elem}"):
                        self.combo_themes.addItem(elem)

    def vmmSettingsOK(self):
        self.frame_vmmSettings.hide()
        self.list_profiles.setEnabled(1)
        self.button_createProfile.setEnabled(1)
        self.frame_profileOptions.setEnabled(1)

        self.theme = self.combo_themes.currentText()
        self.language = self.combo_languages.currentText()[:-5]

        self.setTheme(self.theme)
        self.setLanguage([f"{self.languagePath}/{self.language}.json", f"{self.themePath}/{self.theme}/language.json"][self.theme_config["constLanguage"]])
        self.save()


    def constructStyleSheet(self, allStyle: list, currentObject: dict) -> str:
        styleArray = allStyle.copy()
        if "__all_except" in currentObject.keys():
            for i, elem in enumerate(currentObject["__all_except"]):
                styleArray.pop(elem - i)

        styleArray += currentObject["style"].copy()

        return "\n".join(styleArray)

    def setTheme(self, theme: str):
        if theme not in os.listdir(self.themePath):
            theme = "classic_ru"

        try:
            file = open(f"{self.themePath}/{theme}/theme.json", encoding="utf-8")
        except Exception as Ex:
            self.errMsg(Ex)

        self.theme_config = json.loads(file.read())

        resource_rc = __import__(f"themes.{theme}.resource_rc", fromlist=[None])

        self.bg_profiles.setStyleSheet(self.constructStyleSheet(self.theme_config["bg"]["__all"], self.theme_config["bg"]["profiles"]))
        self.bg_separator.setStyleSheet(self.constructStyleSheet(self.theme_config["bg"]["__all"], self.theme_config["bg"]["separator"]))
        self.bg_options.setStyleSheet(self.constructStyleSheet(self.theme_config["bg"]["__all"], self.theme_config["bg"]["profileOptions"]))
        self.bg_params.setStyleSheet(self.constructStyleSheet(self.theme_config["bg"]["__all"], self.theme_config["bg"]["params"]))

        self.txt_pathGame.setStyleSheet(self.constructStyleSheet(self.theme_config["txt"]["__all"], self.theme_config["txt"]["pathGame"]))
        self.txt_pathInstall.setStyleSheet(self.constructStyleSheet(self.theme_config["txt"]["__all"], self.theme_config["txt"]["pathInstall"]))
        self.txt_comboMod.setStyleSheet(self.constructStyleSheet(self.theme_config["txt"]["__all"], self.theme_config["txt"]["comboMod"]))
        self.txt_delFolder.setStyleSheet(self.constructStyleSheet(self.theme_config["txt"]["__all"], self.theme_config["txt"]["delFolder"]))
        self.txt_copyTo.setStyleSheet(self.constructStyleSheet(self.theme_config["txt"]["__all"], self.theme_config["txt"]["copyTo"]))
        self.txt_comboTheme.setStyleSheet(self.constructStyleSheet(self.theme_config["txt"]["__all"], self.theme_config["txt"]["comboTheme"]))
        self.txt_comboLanguage.setStyleSheet(self.constructStyleSheet(self.theme_config["txt"]["__all"], self.theme_config["txt"]["comboLanguage"]))
        self.txt_version.setStyleSheet(self.constructStyleSheet(self.theme_config["txt"]["__all"], self.theme_config["txt"]["version"]))

        self.edit_pathGame.setStyleSheet(self.constructStyleSheet(self.theme_config["lineedit"]["__all"], self.theme_config["lineedit"]["pathGame"]))
        self.edit_pathInstall.setStyleSheet(self.constructStyleSheet(self.theme_config["lineedit"]["__all"], self.theme_config["lineedit"]["pathInstall"]))
        self.edit_profileName.setStyleSheet(self.constructStyleSheet(self.theme_config["lineedit"]["__all"], self.theme_config["lineedit"]["profileName"]))

        self.list_paramsProfiles.setStyleSheet(self.constructStyleSheet(self.theme_config["list"]["__all"], self.theme_config["list"]["paramsProfiles"]))
        self.list_profiles.setStyleSheet(self.constructStyleSheet(self.theme_config["list"]["__all"], self.theme_config["list"]["profiles"]))

        self.button_createProfile.setStyleSheet(self.constructStyleSheet(self.theme_config["btn"]["__all"], self.theme_config["btn"]["createProfile"]))
        self.button_description.setStyleSheet(self.constructStyleSheet(self.theme_config["btn"]["__all"], self.theme_config["btn"]["description"]))

        self.button_install.setStyleSheet(self.constructStyleSheet(self.theme_config["btn"]["__all"], self.theme_config["btn"]["install"]))
        if self.currentUpdate:
            self.button_install.setStyleSheet(self.constructStyleSheet(self.theme_config["btn"]["__all"], self.theme_config["btn"]["install-update"]))

        self.button_refresh.setStyleSheet(self.constructStyleSheet(self.theme_config["btn"]["__all"], self.theme_config["btn"]["refresh"]))
        self.button_play.setStyleSheet(self.constructStyleSheet(self.theme_config["btn"]["__all"], self.theme_config["btn"]["play"]))
        self.button_params.setStyleSheet(self.constructStyleSheet(self.theme_config["btn"]["__all"], self.theme_config["btn"]["params"]))
        self.button_openFolder.setStyleSheet(self.constructStyleSheet(self.theme_config["btn"]["__all"], self.theme_config["btn"]["openFolder"]))
        self.button_paramsOK.setStyleSheet(self.constructStyleSheet(self.theme_config["btn"]["__all"], self.theme_config["btn"]["paramsOK"]))
        self.button_delete.setStyleSheet(self.constructStyleSheet(self.theme_config["btn"]["__all"], self.theme_config["btn"]["delete"]))
        self.button_yesDel.setStyleSheet(self.constructStyleSheet(self.theme_config["btn"]["__all"], self.theme_config["btn"]["yesDel"]))
        self.button_noDel.setStyleSheet(self.constructStyleSheet(self.theme_config["btn"]["__all"], self.theme_config["btn"]["noDel"]))
        self.button_cancelDel.setStyleSheet(self.constructStyleSheet(self.theme_config["btn"]["__all"], self.theme_config["btn"]["cancelDel"]))
        self.button_vmmSettings.setStyleSheet(self.constructStyleSheet(self.theme_config["btn"]["__all"], self.theme_config["btn"]["vmmSettings"]))
        self.button_vmmSettingsOK.setStyleSheet(self.constructStyleSheet(self.theme_config["btn"]["__all"], self.theme_config["btn"]["vmmSettingsOK"]))
        self.pathButton_game.setStyleSheet(self.constructStyleSheet(self.theme_config["btn"]["__all"], self.theme_config["btn"]["path_game"]))
        self.pathButton_install.setStyleSheet(self.constructStyleSheet(self.theme_config["btn"]["__all"], self.theme_config["btn"]["path_install"]))

        self.combo_bat.setStyleSheet(self.constructStyleSheet(self.theme_config["combo"]["__all"], self.theme_config["combo"]["bat"]))
        self.combo_mods.setStyleSheet(self.constructStyleSheet(self.theme_config["combo"]["__all"], self.theme_config["combo"]["mod"]))
        self.combo_themes.setStyleSheet(self.constructStyleSheet(self.theme_config["combo"]["__all"], self.theme_config["combo"]["theme"]))
        self.combo_languages.setStyleSheet(self.constructStyleSheet(self.theme_config["combo"]["__all"], self.theme_config["combo"]["language"]))

        self.check_paramsOptions.setStyleSheet(self.constructStyleSheet(self.theme_config["check"]["__all"], self.theme_config["check"]["paramsOptions"]))
        self.check_paramsControls.setStyleSheet(self.constructStyleSheet(self.theme_config["check"]["__all"], self.theme_config["check"]["paramsControls"]))
        self.check_save00.setStyleSheet(self.constructStyleSheet(self.theme_config["check"]["__all"], self.theme_config["check"]["save00"]))
        self.check_save01.setStyleSheet(self.constructStyleSheet(self.theme_config["check"]["__all"], self.theme_config["check"]["save01"]))
        self.check_save02.setStyleSheet(self.constructStyleSheet(self.theme_config["check"]["__all"], self.theme_config["check"]["save02"]))
        self.check_save03.setStyleSheet(self.constructStyleSheet(self.theme_config["check"]["__all"], self.theme_config["check"]["save03"]))
        self.check_save04.setStyleSheet(self.constructStyleSheet(self.theme_config["check"]["__all"], self.theme_config["check"]["save04"]))
        self.check_save05.setStyleSheet(self.constructStyleSheet(self.theme_config["check"]["__all"], self.theme_config["check"]["save05"]))
        self.check_save06.setStyleSheet(self.constructStyleSheet(self.theme_config["check"]["__all"], self.theme_config["check"]["save06"]))
        self.check_save07.setStyleSheet(self.constructStyleSheet(self.theme_config["check"]["__all"], self.theme_config["check"]["save07"]))
        self.check_save08.setStyleSheet(self.constructStyleSheet(self.theme_config["check"]["__all"], self.theme_config["check"]["save08"]))

        self.errorMessage.setStyleSheet("\n".join(self.theme_config["win"]["errorMessage"]["window"]))
        self.errorMessage.buttons()[0].setStyleSheet("\n".join(self.theme_config["win"]["errorMessage"]["button"]))

        self.infoMessage.setStyleSheet("\n".join(self.theme_config["win"]["infoMessage"]["window"]))
        self.infoMessage.buttons()[0].setStyleSheet("\n".join(self.theme_config["win"]["infoMessage"]["button"]))

        self.modDescription.setStyleSheet("\n".join(self.theme_config["win"]["modDescription"]["window"]))
        self.modDescription.buttons()[0].setStyleSheet("\n".join(self.theme_config["win"]["modDescription"]["button"]))

        self.vmmUpdate.setStyleSheet("\n".join(self.theme_config["win"]["vmmUpdate"]["window"]))
        self.button_update.setStyleSheet("\n".join(self.theme_config["win"]["vmmUpdate"]["update"]))
        self.button_later.setStyleSheet("\n".join(self.theme_config["win"]["vmmUpdate"]["later"]))

        for item in range(self.list_profiles.count()):
            self.list_profiles.item(item).setBackground(QtGui.QColor(self.theme_config["listelem"]["profiles"]["background"]))
            self.list_profiles.item(item).setForeground(QtGui.QColor(self.theme_config["listelem"]["profiles"]["text"]))

    def setLanguage(self, languagePath: str):
        if not os.path.exists(languagePath):
            languagePath = f"{self.themePath}/classic_ru/language.json"

        try:
            file = open(languagePath, encoding="utf-8")
        except Exception as Ex:
            self.errMsg(Ex)

        self.language_config = json.loads(file.read())

        self.errorMessage.setWindowTitle(self.language_config["titles"]["errorMessage"])
        self.infoMessage.setWindowTitle(self.language_config["titles"]["infoMessage"])
        self.vmmUpdate.setWindowTitle(self.language_config["titles"]["vmmUpdate"])
        self.modDescription.setWindowTitle(self.language_config["titles"]["modDescription"])

        self.txt_pathGame.setText(self.language_config["txt"]["pathGame"])
        self.txt_pathInstall.setText(self.language_config["txt"]["pathInstall"])
        self.txt_comboMod.setText(self.language_config["txt"]["comboMod"])
        self.txt_delFolder.setText(self.language_config["txt"]["delFolder"])
        self.txt_copyTo.setText(self.language_config["txt"]["copyTo"])
        self.txt_comboTheme.setText(self.language_config["txt"]["comboTheme"])
        self.txt_comboLanguage.setText(self.language_config["txt"]["comboLanguage"])

        self.button_createProfile.setText(self.language_config["btn"]["createProfile"])
        self.button_description.setText(self.language_config["btn"]["description"])

        self.button_install.setText(self.language_config["btn"]["install"])
        if self.currentUpdate:
            self.button_install.setText(self.language_config["btn"]["install-update"])

        self.button_refresh.setText(self.language_config["btn"]["refresh"])
        self.button_play.setText(self.language_config["btn"]["play"])
        self.button_params.setText(self.language_config["btn"]["params"])
        self.button_openFolder.setText(self.language_config["btn"]["openFolder"])
        self.button_paramsOK.setText(self.language_config["btn"]["paramsOK"])
        self.button_delete.setText(self.language_config["btn"]["delete"])
        self.button_yesDel.setText(self.language_config["btn"]["yesDel"])
        self.button_noDel.setText(self.language_config["btn"]["noDel"])
        self.button_cancelDel.setText(self.language_config["btn"]["cancelDel"])
        self.button_vmmSettings.setText(self.language_config["btn"]["vmmSettings"])
        self.button_vmmSettingsOK.setText(self.language_config["btn"]["vmmSettingsOK"])
        self.pathButton_game.setText(self.language_config["btn"]["path_game"])
        self.pathButton_install.setText(self.language_config["btn"]["path_install"])

        self.check_paramsOptions.setText(self.language_config["check"]["paramsOptions"])
        self.check_paramsControls.setText(self.language_config["check"]["paramsControls"])

        self.vmmUpdate.setText(self.language_config["vmmUpdate"]["message"])
        self.button_update.setText(self.language_config["vmmUpdate"]["update"])
        self.button_later.setText(self.language_config["vmmUpdate"]["later"])


    def refresh(self):
        self.setTheme(self.theme)
        self.setLanguage([f"{self.languagePath}/{self.language}.json", f"{self.themePath}/{self.theme}/language.json"][self.theme_config["constLanguage"]])

        try:
            vmm_response = get("https://api.github.com/repos/XiadaOku/VMM/releases").json()[0]
        except Exception as msg:
            self.errMsg(msg)

        if vmm_version != vmm_response["tag_name"]:
            text = vmm_response["body"].split("\r\n")
            if f"[{self.language_config['outerLanguage']}]" in text:
                ind = text.index(f"[{self.language_config['outerLanguage']}]")
            else:
                ind = text.index("[ru]")

            description = ""
            for line in range(ind + 1, len(text)):
                if len(text[line]) >= 2 and text[line][0] == "[" and text[line][-1] == "]":
                    break
                description += text[line] + "\n"

            self.vmmUpdate.setText(self.language_config["vmmUpdate"]["message"] % (vmm_response["tag_name"], description, vmm_version))

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
                    elif sys.platform == "linux":
                        pid = os.fork()
                        if pid == 0:
                            os.system("nohup python3 ./src/update.py &")
                else:
                    if sys.platform == "win32":
                        os.system("start python ../client/update.py")
                    elif sys.platform == "linux":
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
        for idMod in self.response:
            self.combo_mods.addItem(self.response[idMod]["name"]["ru"])
            self.nameToModID.update({self.response[idMod]["name"]["ru"]: idMod})

        if mod_id == "none":
            self.combo_mods.setCurrentText("None")
        else:
            self.combo_mods.setCurrentText(self.response[mod_id]["name"]["ru"])

        isOldId = 0
        for id in range(len(self.mods_array)):
            if isinstance(self.mods_array[id]["mod"], int):
                if self.mods_array[id]["mod"] == 0:
                    self.mods_array[id]["mod"] = "none"
                else:
                    self.mods_array[id]["mod"] = list(self.response.keys())[self.mods_array[id]["mod"] - 1]
                isOldId = 1
        if isOldId:
            self.inner_mods_array = []
            for elem in self.mods_array:
                self.inner_mods_array.append(elem.copy())

            self.save()


    def createProfile(self):
        profile = QtWidgets.QListWidgetItem()
        profile.setTextAlignment(0)
        profile.setBackground(QtGui.QColor(self.theme_config["listelem"]["profiles"]["background"]))
        profile.setForeground(QtGui.QColor(self.theme_config["listelem"]["profiles"]["text"]))
        profile.setText(self.language_config["modName"]["newModName"])

        self.list_profiles.addItem(profile)

        self.mods_array.append({"name": self.language_config["modName"]["newModName"],
                                "vangersPath": pathToVangers, "mod": "none", "installPath": "", "modVersion": -1})
        self.inner_mods_array.append({"name": self.language_config["modName"]["newModName"],
                                      "vangersPath": pathToVangers, "mod": "none", "installPath": "", "modVersion": -1})

        self.save()

    def deleteProfile(self):
        if self.list_profiles.currentItem() and self.list_profiles.currentItem().text() == self.edit_profileName.text():
            if self.mods_array[self.list_profiles.currentRow()]["modVersion"]:
                if os.path.exists(self.mods_array[self.list_profiles.currentRow()]["installPath"] +
                                  "/Vangers [" + self.mods_array[self.list_profiles.currentRow()]["name"] + "]"):
                    self.frame_delFolder.show()

                    self.list_profiles.setEnabled(0)
                    self.button_createProfile.setEnabled(0)
                    self.frame_profileOptions.setEnabled(0)
                else:
                    self.mods_array.pop(self.list_profiles.currentRow())
                    self.inner_mods_array.pop(self.list_profiles.currentRow())
                    self.list_profiles.takeItem(self.list_profiles.currentRow())

                    self.save()
            else:
                self.mods_array.pop(self.list_profiles.currentRow())
                self.inner_mods_array.pop(self.list_profiles.currentRow())
                self.list_profiles.takeItem(self.list_profiles.currentRow())

                self.save()

    def delete_folder(self):
        shutil.rmtree(self.mods_array[self.list_profiles.currentRow()]["installPath"] +
                      "/Vangers [" + self.mods_array[self.list_profiles.currentRow()]["name"] + "]")
        self.mods_array.pop(self.list_profiles.currentRow())
        self.inner_mods_array.pop(self.list_profiles.currentRow())
        self.list_profiles.takeItem(self.list_profiles.currentRow())

        self.frame_delFolder.hide()
        self.list_profiles.setEnabled(1)
        self.button_createProfile.setEnabled(1)
        self.frame_profileOptions.setEnabled(1)

        self.save()

    # "оставление". отлично же
    def save_folder(self):
        self.mods_array.pop(self.list_profiles.currentRow())
        self.inner_mods_array.pop(self.list_profiles.currentRow())
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
        if mod_id == "none":
            description = self.language_config["modName"]["none_description"]
        else:
            if self.response[mod_id]["site"]:
                link_button = self.modDescription.addButton(self.language_config["desc"]["webPage"], QtWidgets.QMessageBox.ActionRole)
                link_button.setStyleSheet("\n".join(self.theme_config["win"]["modDescription"]["button"]))

            if self.language_config["outerLanguage"] in self.response[mod_id]["name"] and \
                    self.response[mod_id]["name"][self.language_config["outerLanguage"]] != "":
                name = self.response[mod_id]["name"][self.language_config["outerLanguage"]]
            else:
                name = self.response[mod_id]["name"]["ru"]

            if self.language_config["outerLanguage"] in self.response[mod_id]["description"] and \
                    self.response[mod_id]["description"][self.language_config["outerLanguage"]] != "":
                desc = self.response[mod_id]["description"][self.language_config["outerLanguage"]]
            else:
                desc = self.response[mod_id]["description"]["ru"]

            description = "[" + name + "]\n\n" + desc + "\n\n" + self.language_config["desc"]["authors"] + \
                          ", ".join(self.response[mod_id]["author"]) + "\n\n"

            if len(self.response[mod_id]["contacts"]):
                description += self.language_config["desc"]["contacts"] + \
                               ", ".join(self.response[mod_id]["contacts"]) + "\n\n"

            description += self.language_config["desc"]["version"] + self.response[mod_id]["version"]

        self.modDescription.setText(description)

        self.modDescription.exec()

        if mod_id != "none" and self.response[mod_id]["site"] and self.modDescription.clickedButton() == link_button:
            webbrowser.open(self.response[mod_id]["site"])

        if mod_id != "none" and self.response[mod_id]["site"]:
            self.modDescription.removeButton(link_button)

    def install(self):
        if self.list_profiles.currentItem() and self.list_profiles.currentItem().text() == self.edit_profileName.text():
            if self.edit_pathGame.text() and self.edit_pathInstall.text():
                if not os.path.exists(self.edit_pathInstall.text()):
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
                    text += self.language_config["error"]["vangersPathNone"] + "\n"
                if not self.edit_pathInstall.text():
                    text += self.language_config["error"]["installPathNone"]

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
                elif sys.platform == "linux":
                    os.system("sudo bash " + self.mods_array[id]["installPath"] + "/Vangers [" +
                              self.mods_array[id]["name"] + "]/" + self.launchFileNames[self.combo_bat.currentText()])
                os.chdir(cwd)
            else:
                text = ""

                if self.mods_array[id]["modVersion"] == -1:
                    text += self.language_config["error"]["modNotInstalled"] + "\n"

                if self.combo_bat.currentText() == "":
                    text += self.language_config["error"]["batNotChosen"]

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

                if os.path.exists(self.mods_array[mod_id]["installPath"] + "/Vangers [" +
                                  self.mods_array[mod_id]["name"] + "]/data/savegame"):
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
                else:
                    self.infoMessage.setText(self.language_config["error"]["folderNotFound"])
                    self.infoMessage.exec()
                    return

                self.frame_paramsTransition.show()
                self.list_profiles.setEnabled(0)
                self.button_createProfile.setEnabled(0)

                self.list_paramsProfiles.clear()
                for profile in range(self.list_profiles.count()):
                    new_profile = QtWidgets.QListWidgetItem(self.inner_mods_array[profile]["name"])
                    new_profile.setTextAlignment(0)
                    new_profile.setBackground(QtGui.QColor(self.theme_config["listelem"]["paramsProfiles"]["background"]))
                    new_profile.setForeground(QtGui.QColor(self.theme_config["listelem"]["paramsProfiles"]["text"]))

                    self.list_paramsProfiles.addItem(new_profile)
                    self.list_paramsProfiles.item(profile).setHidden(1)

                    if profile == self.list_profiles.currentRow():
                        continue
                    if self.mods_array[profile]["installPath"]:
                        if os.path.exists(self.mods_array[profile]["installPath"] + "/Vangers [" +
                                          self.mods_array[profile]["name"] + "]/data/savegame"):
                            self.list_paramsProfiles.item(profile).setHidden(0)

            else:
                self.infoMessage.setText(self.language_config["error"]["modNotInstalled"])
                self.infoMessage.exec()

    def paramsOK(self):
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
        self.list_profiles.currentItem().setText(self.inner_mods_array[self.list_profiles.currentRow()]["name"])
        self.edit_profileName.setText(self.inner_mods_array[self.list_profiles.currentRow()]["name"])
        self.edit_pathGame.setText(self.inner_mods_array[self.list_profiles.currentRow()]["vangersPath"])
        self.edit_pathInstall.setText(self.inner_mods_array[self.list_profiles.currentRow()]["installPath"])

        if self.inner_mods_array[self.list_profiles.currentRow()]["mod"] == "none":
            self.combo_mods.setCurrentText("None")
        else:
            self.combo_mods.setCurrentText(self.response[self.inner_mods_array[self.list_profiles.currentRow()]["mod"]]["name"]["ru"])

        self.launchFileNames = {"Windows 32bit (русский)": "Win32_ru.bat", "Windows 64bit (русский)": "Win64_ru.bat",
                                "Windows 32bit (english)": "Win32_en.bat",
                                "Windows 64bit (english)": "Win64_en.bat", "Linux (русский)": "Linux_ru.sh",
                                "Linux (english)": "Linux_en.sh"}

        self.combo_bat.clear()

        mod_id = self.list_profiles.currentRow()
        for bat in range(len(self.launchFileNames)):
            if self.mods_array[self.list_profiles.currentRow()]["mod"] != "none":
                lresponse = self.response[self.mods_array[mod_id]["mod"]]["launch"]
                if lresponse[list(lresponse.keys())[bat]] != "":
                    self.launchFileNames[list(self.launchFileNames.keys())[bat]] = lresponse[list(lresponse.keys())[bat]]
            self.combo_bat.addItem(list(self.launchFileNames.keys())[bat])

        if self.mods_array[mod_id]["mod"] != "none":
            if self.response[self.mods_array[mod_id]["mod"]]["version"] != \
                    self.mods_array[mod_id]["modVersion"] and self.mods_array[mod_id]["modVersion"] != -1:

                self.button_install.setStyleSheet(self.constructStyleSheet(self.theme_config["btn"]["__all"], self.theme_config["btn"]["install-update"]))
                self.button_install.setText(self.language_config["btn"]["install-update"])

                self.currentUpdate = True
            else:
                self.button_install.setStyleSheet(self.constructStyleSheet(self.theme_config["btn"]["__all"], self.theme_config["btn"]["install"]))
                self.button_install.setText(self.language_config["btn"]["install"])

                self.currentUpdate = False

    def openFolder(self):
        path = self.mods_array[self.list_profiles.currentRow()]["installPath"] + "/Vangers [" + \
               self.mods_array[self.list_profiles.currentRow()]["name"] + "]/data/savegame"
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "linux":
            os.system("xdg-open " + path)

    def nameEdited(self, text):
        if self.list_profiles.currentItem():
            self.list_profiles.currentItem().setText(text)
            self.inner_mods_array[self.list_profiles.currentRow()]["name"] = text

    def pathGame(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory()
        if folder:
            self.edit_pathGame.setText(folder)
            if self.list_profiles.currentItem():
                self.inner_mods_array[self.list_profiles.currentRow()]["vangersPath"] = folder

    def pathInstall(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory()
        if folder:
            self.edit_pathInstall.setText(folder)
            if self.list_profiles.currentItem():
                self.inner_mods_array[self.list_profiles.currentRow()]["installPath"] = folder

    def pathGameChanged(self, text):
        if self.list_profiles.currentItem():
            self.inner_mods_array[self.list_profiles.currentRow()]["vangersPath"] = text

    def pathInstallChanged(self, text):
        if self.list_profiles.currentItem():
            self.inner_mods_array[self.list_profiles.currentRow()]["installPath"] = text

    def comboModsChanged(self, text):
        if self.list_profiles.currentItem() and text != "":
            self.inner_mods_array[self.list_profiles.currentRow()]["mod"] = self.nameToModID[text]



def main():
    # Adding "." and ".." to the PYTHONPATH for themes folder (resource_rc.py files)
    sys.path.append(os.path.realpath("."))
    sys.path.append(os.path.realpath(".."))

    # одномониторная недоподдержка high-dpi
    if sys.platform == "win32":
        dpi = ctypes.windll.shcore.GetScaleFactorForDevice(1) / 100
        os.environ["QT_SCREEN_SCALE_FACTORS"] = str(dpi)

    app = QtWidgets.QApplication(sys.argv)
    window = VMM()
    window.show()
    app.exec_()


if __name__ == '__main__':
    launchFiles = {"Win32_ru.bat": "@echo off \ncd data \n.\\..\\bin\\windows-32\\vangers.exe -russian",
                   "Win64_ru.bat": "@echo off \ncd data \n.\\..\\bin\\windows-64\\vangers.exe -russian",
                   "Win32_en.bat": "@echo off \ncd data \n.\\..\\bin\\windows-32\\vangers.exe",
                   "Win64_en.bat": "@echo off \ncd data \n.\\..\\bin\\windows-64\\vangers.exe",
                   "Linux_ru.sh": "#!/bin/sh \nBASEDIR=$(pwd) \nexport " +
                                  "LD_LIBRARY_PATH=$BASEDIR/bin/linux/lib64:$LD_LIBRARY_PATH \ncd data \n" +
                                  "./../bin/linux/vangers64 -russian",
                   "Linux_en.sh": "#!/bin/sh \nBASEDIR=$(pwd) \nexport " +
                                  "LD_LIBRARY_PATH=$BASEDIR/bin/linux/lib64:$LD_LIBRARY_PATH \ncd data \n" +
                                  "./../bin/linux/vangers64"
                   }


    pathToVangers = ""

    # Поиск папки в стиме
    drive = os.getcwd()[:os.getcwd().find("\\")]
    if os.path.exists(drive + "/Program Files (x86)/Steam/SteamApps/Common/Vangers"):
        pathToVangers = drive + "/Program Files (x86)/Steam/SteamApps/Common/Vangers"
    elif os.path.exists(drive + "/Program Files/Steam/SteamApps/Common/Vangers"):
        pathToVangers = drive + "/Program Files/Steam/SteamApps/Common/Vangers"

    main()
