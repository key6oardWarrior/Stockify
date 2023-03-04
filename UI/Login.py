from PySimpleGUI.PySimpleGUI import Button, Input, InputText, Text, Window

from Helper.creds import winName
from Helper.helper import exitApp

def loginScreen() -> None:
	layout = [
		[Text("Enter your robinhood email address: "), Input(key="email", size=(30, 1))],
		[Text("Enter your robinhood password: "), InputText("",
			key="password", password_char="*", size=(15, 1), do_not_clear=False)],
		[Button("Submit"), Button("Exit")]
	]

	login = Window(winName, layout, modal=True)

	while True:
		event, values = login.read()
		exitApp(event, login)

		if event == "Submit":
			login.close()

def signUpScreen() -> None:
	layout = [
		[Text("Enter your robinhood email address: "), Input(key="email")],
		[Text("Enter your robinhood password: "), Input("", key="password",
			password_char="*", do_not_clear=False)],
		[Text("Enter your credit card number: "), Input("", key="ccn")],
		[Text("Enter credit card code: "), Input("", key="code",
			password_char="*")],
		[Text("State: "), Input("", key="state")],
		[Text("City: "), Input("", key="city")],
		[Text("Address: "), Input("", key="addy")],
		[Text("Zip Code: "), Input("", key="zip")],
		[Text("First Name: "), Input("", key="fName")],
		[Text("Last Name: "), Input("", key="lName")],
		[Text("Expiration Data"), Input("", key="exp")],

		[Button("Submit"), Button("Exit")]
	]

	signUp = Window(winName, layout, modal=True)

	while True:
		event, values = signUp.read()
		exitApp(event, signUp)

		signUp.close()