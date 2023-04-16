from Helper.helper import Version, exitApp, exit
from Helper.creds import winName
from requests import get
from wget import download
from PyGUI import Text, Button, Window, FolderBrowse
from os.path import isdir

def updateScreen() -> bool:
	layout = []
	responce = get("https://github.com/key6oardWarrior/Stockify/blob/main/version.txt")
	version = Version()

	if responce.status_code == 200:
		if version.version == responce.text:
			layout.append([Text("You have the most up to date version of this software :)")])
		else:
			layout.append([Text("There is a new version of this software. Where would you like to download it:")])
			layout.append([FolderBrowse(key="browse"), Button("Submit"), Button("Back")])

	SIZE = len(layout)

	while True:
		if len(layout) > SIZE:
			layout = layout[:-1]

		update = Window(winName, layout)
		event, values = update.read()

		if exitApp(event, update):
			exit(0)

		if event == "Back":
			return True

		if event == "Submit":
			if isdir(values["browse"]):
				try:
					download("https://github.com/key6oardWarrior/Stockify/" \
						f"archive/refs/tags/{version.version}.zip",
						values["browse"]
					)
				except:
					layout.append([Text("Check you internet connection", text_color="red")])
				else:
					win = Window(winName, [[Text("To update this app close this app and run the downloaded app"), Button("Ok")]])
					win.read()
					win.close()
					return False
			else:
				layout.append([Text("The folder location selected is not a folder", text_color="red")])
