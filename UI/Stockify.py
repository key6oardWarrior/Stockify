from sys import path, platform
path.append(path[0][:path[0].rfind("\\")]) # not production

# add path to needed libs
if platform == "win32":
	from os.path import expanduser
	path.append(expanduser("~") + "\\AppData\\Local\\Stockify\\UI")
	path.append(expanduser("~") + "\\AppData\\Local\\Stockify")
elif((platform == "linux") or (platform == "linux2")):
	path.append("/usr/local/Stockify/bins")
else: # darwin
	path.append("/usr/local/bin/Stockify/bins")

from PySimpleGUI.PySimpleGUI import Button, Text, Window

from Login import loginScreen, signUpScreen
from TradeInfo import dataScreen
from Helper.helper import exitApp, exit
from Helper.creds import winName

def landing():
	layout = [
		[Button("Login", pad=((39, 5), (0, 0))), Button("Sign Up"), Button("How to Use")],
		[Text("Powered by Robin_Stocks, Authorize.Net,", text_color="light gray")],
		[Text("and PySimpleGUI", text_color="light gray", pad=((71, 0), (0, 0)))]
	]
	isBack = True

	while isBack:
		landingPage = Window(winName, layout, modal=True)
		event, values = landingPage.read()

		if exitApp(event, landingPage):
			exit(0)

		landingPage.close()
		if event == "Login":
			isBack = loginScreen()
		elif event == "Sign Up":
			isBack = signUpScreen()

landing()
dataScreen()