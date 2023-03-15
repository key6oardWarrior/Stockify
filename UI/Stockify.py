from sys import path, platform
path.append(path[0][:path[0].rfind("\\")]) # not production

# add path to needed libs
if platform == "win32":
	from os.path import expanduser
	path.append(expanduser("~") + "\\AppData\\Local\\Stockify")
elif((platform == "linux") or (platform == "linux2")):
	path.append("/usr/local/Stockify")
else: # darwin
	path.append("/usr/local/bin/Stockify")

from PySimpleGUI.PySimpleGUI import Button, Window

from Login import loginScreen, signUpScreen
from TradeInfo import dataScreen
from Helper.helper import exitApp, exit
from Helper.creds import winName

def landing():
	layout = [
		[Button("Login"), Button("Sign Up"), Button("How to Use")]
	]

	landingPage = Window(winName, layout, modal=True)

	event, values = landingPage.read()
	if exitApp(event, landingPage):
		exit(0)
	landingPage.close()

	if event == "Login":
		loginScreen()
	else:
		signUpScreen()

landing()
dataScreen()