from Helper.helper import Version, exitApp, exit
from Helper.creds import winName
from requests import get
from wget import download
from PyGUI import Text, Button, Window, FolderBrowse
from os.path import isdir, exists, join
from sys import platform

def _setLayout(version: Version) -> list[list]:
	'''
	Create the update screen's layout

	# Params:
	version - Version object that determins the user's current app version

	# Returns:
	A 2D list that determins what the update screen will look like
	'''
	layout = []
	version_str = ""

	try:
		responce = get("https://raw.githubusercontent.com/key6oardWarrior/Stockify_Release/main/version.txt")	
	except:
		layout.append([Text("Check your internet connection", text_color="red")])
		layout.append([Button("Retry"), Button("Back")])
	else:
		if responce.status_code == 200:
			version_str = responce.text.strip("\n")

			if version.version == version_str:
				layout.append([Text("You have the most up to date version of this software :)")])
				layout.append([Button("Back")])
			else:
				layout.append([Text("There is a new version of this software. Where would you like to download it:"), FolderBrowse(key="browse")])
				layout.append([Button("Submit"), Button("Back")])
		else:
			layout.append([Text("Something when wrong please try again", text_color="red")])
			layout.append([Button("Retry"), Button("Back")])

	return layout, version_str

def updateScreen() -> None:
	version = Version()
	layout, version_str = _setLayout(version)
	size = len(layout)

	while True:
		update = Window(winName, layout)
		event, values = update.read()

		if exitApp(event, update):
			exit(0)

		if len(layout) > size:
			layout = layout[:-1]

		if event == "Back":
			update.close()
			return

		if event == "Submit":
			# format string for Windows OS
			if platform == "win32":
				values["browse"] = values["browse"].replace("/", "\\")

			if isdir(values["browse"]):
				PKG_NAME = f"{version_str}.zip"
				FILE_NAME = join(values["browse"], f"Stockify{PKG_NAME}")

				if exists(join(values["browse"], FILE_NAME)):
					win = Window(winName, [[Text("The folder you selected already has the lastest version downloaded. Run the installer in that folder.", text_color="red")], [Button("Ok")]], modal=True)
					win.read()
					win.close()
					update.close()
					return

				try:
					download("https://github.com/key6oardWarrior/" \
						f"Stockify_Release/archive/refs/tags/{PKG_NAME}",
						FILE_NAME
					)
				except:
					layout.append([Text("Check you internet connection", text_color="red")])
					update.close()
				else:
					win = Window(winName, [[Text("To update this app close this app and run the installer"), Button("Ok")]], modal=True)
					win.read()
					win.close()
					update.close()
					return
			else:
				layout.append([Text("The folder location selected is not a folder", text_color="red")])
				update.close()

		elif event == "Retry":
			layout = _setLayout(version)
			size = len(layout)
			update.close()
