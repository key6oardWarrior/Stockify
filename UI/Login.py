from PySimpleGUI.PySimpleGUI import Button, Input, Text, Window

from Helper.creds import winName
from Helper.helper import exitApp, exit

from Robinhood_API.Login import UserAuth

def loginScreen() -> bool:
	'''
	# Returns:
	True if user has logged in successfuly. False if user clicks back button
	'''
	layout = [
		[Text("Enter your robinhood email address:"), Input(key="email", size=(30, 1))],
		[Text("Enter your robinhood password:"), Input("",
			key="password", password_char="*", size=(15, 1), do_not_clear=False)],
		[Text("Enter two factor authentication code. If one is not needed leave blank:"), Input(key="mfa")],
		[Button("Submit", key="submit"), Button("Back", key="back")]
	]

	login = Window(winName, layout, modal=True)
	userAuth = UserAuth()
	SIZE = len(layout)

	while userAuth.isLoggedIn == False:
		event, values = login.read()
		if exitApp(event, login):
			exit(0)

		if len(layout) > SIZE:
			del layout[-1]

		if event == "submit":
			if((values["email"] == "") or (values["password"] == "")):
				layout.append([Text("Enter your email and password to login", text_color="red")])
				login.close()
				login = Window(winName, layout)
				continue

			try:
				userAuth.login(values["email"], values["password"], values["mfa"])
			except Exception as e:
				layout.append([Text(e, text_color="red")])

			login.close()
		elif event == "back":
			login.close()
			return True

	return False

def signUpScreen() -> bool:
	'''
	# Returns:
	True if user has signed up successfuly. False if user clicks back button
	'''
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
		if exitApp(event, signUp):
			exit(0)

		signUp.close()
		break