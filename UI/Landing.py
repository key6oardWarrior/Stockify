from sys import path
path.append(path[0][:path[0].rfind("\\")])

from PySimpleGUI.PySimpleGUI import Button, Window

from Login import loginScreen, signUpScreen
from TradeInfo import dataScreen
from Helper.helper import exitApp
from Helper.creds import winName

def landing():
	layout = [
		[Button("Login"), Button("Sign Up"), Button("Exit")]
	]

	landingPage = Window(winName, layout, modal=True)

	while True:
		event, values = landingPage.read()
		exitApp(event, landingPage)
		landingPage.close()

		if event == "Login":
			loginScreen()
		else:
			signUpScreen()

		break

# landing()
dataScreen()