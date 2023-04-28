from PyGUI import Button, Input, Text, Window

from Helper.creds import winName
from Helper.helper import exitApp, exit, getPayment, checkConnection, \
	userAuth, killApp
from ServerSide.DataBase import DataBase

from Helper.Errors import IncorrectPassword, UserAlreadyExist

from shutil import rmtree
from os.path import join, expanduser
from requests import get
from json import loads
from datetime import datetime
from hashlib import sha256

def _getNextMonth() -> datetime:
	'''
	Determin the date for one month from now

	# Returns:
	A datatime object that contains next month's date
	'''
	today = datetime.today()

	if today.month < 11:
		nextMonth = datetime(today.year, today.month+1, today.day)
	else:
		nextMonth = datetime(today.year+1, today.month+1, today.day)

	return nextMonth

def attemptLogin(email: str, password: str, mfa: str=None) -> None:
	if mfa == "":
		mfa = None
	userAuth.login(email, password, mfa)

def _collectPayment(values: dict[str, str], isCharging: bool) -> tuple[bool, str]:
	'''
	Either charge the credit card, or check if it is valid

	# Params:
	values - All the user's credit card details\n
	isCharging - True if charging credit card else false

	# Returns:
	tuple[0] = if successful, tuple[1] = error code
	'''
	try: # check if credit card is valid before charing
		code: tuple[bool, str] = getPayment(values["email"], values["ccn"], values["code"],
			values["state"], values["city"], values["addy"], values["zip"],
			values["exp"], values["fName"], values["lName"], isCharging)
	except:
		return (False, "Payment failed please try again")

		# get all of Authorize.Net's responce codes and display error message
	if code[0] == False:
		try:
			responceCodes = loads(get("https://developer.authorize.net/api/reference/dist/json/responseCodes.json").text)
		except:
			return (False, "Payment failed please try again")

		for rc in responceCodes:
			if code[1] == rc["code"]:
				return (False, rc["text"])

	return code

def loginScreen() -> bool:
	'''
	# Returns:
	True if user has logged in successfuly. False if user clicks back button
	'''
	layout = [
		[Text("Enter your robinhood email address:"), Input(key="email", size=(30, 1))],
		[Text("Enter your password:"), Input("",
			key="password", password_char="*", size=(15, 1), do_not_clear=False)],
		[Text("Enter two factor authentication code. If one is not needed leave blank:"), Input(key="mfa")],
		[Button("Submit", key="submit"), Button("Back", key="back")]
	]

	updateLayout = [
		[Text("Enter your credit card number:"), Input("", key="ccn")],
		[Text("Enter credit card code:"), Input("", key="code",
			password_char="*")],
		[Text("State:"), Input("", key="state")],
		[Text("City:"), Input("", key="city")],
		[Text("Address:"), Input("", key="addy")],
		[Text("Zip Code:"), Input("", key="zip")],
		[Text("First Name:"), Input("", key="fName")],
		[Text("Last Name:"), Input("", key="lName")],
		[Text("Expiration Date (YYYY-MM):"), Input("", key="exp")],
		[Button("Submit", key="o_submit"), Button("Back", key="o_back")]
	]

	db = DataBase()

	login = Window(winName, layout)
	SIZE = len(layout)

	while userAuth.isLoggedIn == False:
		rmtree(join(expanduser("~"), ".tokens"), ignore_errors=True)
		event, values = login.read()

		if exitApp(event, login, True):
			exit(0)

		if len(layout) > SIZE:
			del layout[-1]

		try:
			checkConnection()
		except:
			layout.append([Text("Check Internet Connection", text_color="red")])
			login = Window(winName, layout)
			continue

		if db.isConnected == False:
			db.connect()

		if event == "submit":
			values["email"] = values["email"].strip()
			values["mfa"] = values["mfa"].strip()

			if((values["email"] == "") or (values["password"] == "")):
				layout.append([Text("Enter your email and password to login", text_color="red")])
				login.close()
				login = Window(winName, layout)
				continue

			if db.isConnected == False:
				login.close()
				layout.append([Text("Check Internet Connection", text_color="red")])
				login = Window(winName, layout)
				continue

			try: # if internet goes out
				if db.findUsers({"Email": values["email"]}) == []:
					layout.append([Text("User {} not found. You many need to sign up".format(values["email"]), text_color="red")])
					login.close()
					login = Window(winName, layout)
					continue

				db.decrypt(values["email"], values["password"])
				userData: dict = db.userData
				today: datetime = datetime.today()
			except IncorrectPassword as IP:
				login.close()
				layout.append([Text("The password you enterd is incorrect", text_color="red")])
				login = Window(winName, layout)
				continue
			except:
				login.close()
				layout.append([Text("Check Internet Connection", text_color="red")])
				login = Window(winName, layout)
				continue

			if((userData["Was Last Payment Recieved"] == False) or
				(
					(userData["Pay date"].year <= today.year) and
					(userData["Pay date"].month <= today.month) and
					(userData["Pay date"].day <= today.day)
				)
			):
				try:
					db.updateUser({"Email": values["email"]},
						{"Was Last Payment Recieved": False}, values["password"])
				except IncorrectPassword as ip:
					login.close()
					layout.append([Text(ip.args[1], text_color="red")])
					login = Window(winName, layout)
					continue
				except UserAlreadyExist as uae:
					login.close()
					layout.append([Text(uae.args[1], text_color="red")])
					login = Window(winName, layout)
					continue
				except:
					login.close()
					layout.append([Text("Check Internet Connection", text_color="red")])
					login = Window(winName, layout)
					continue

				o_layout = [
					[Text("Do your bill is past due. Would you like to pay it now")],
					[Button("Yes, pay now", key="pay"), Button("No", key="no_pay"), Button("Update payment info", key="update")]
				]
				overlayed = Window(winName, o_layout, modal=True)

				while True:
					o_event, o_values = overlayed.read()

					if exitApp(o_event, overlayed):
						overlayed.close()
						break

					o_layout = [
						[Text("Do your bill is past due. Would you like to pay it now")],
						[Button("Yes, pay now", key="pay"), Button("No", key="no_pay"), Button("Update payment info", key="update")]
					]

					if o_event == "no_pay":
						killApp()

					if o_event == "pay":
						douleOverlayed = Window(winName, [[Text("Verify Credit Card Code:"), Input(key="code")], [Button("Submit")]], modal=True)
						oo_event, oo_values = douleOverlayed.read()

						if ((exitApp(oo_event, douleOverlayed)) or
							(sha256(oo_values["code"].encode()).hexdigest() != userData["Code"])):
							douleOverlayed.close()
							o_layout.append([Text("Incorrect Credit Card Code", text_color="red")])
							continue

						code: tuple[bool, str] = _collectPayment(values, True)
						douleOverlayed.close()

						if code[0]:
							overlayed.close()
						else:
							o_layout.append([Text(code[1], text_color="red")])
							overlayed.close()
							overlayed = Window(winName, layout, modal=True)
							continue

						# update user's data
						db.decrypt(values["email"], values["password"])
						newValues = {
							"Pay date": _getNextMonth(),
							"Was Last Payment Recieved": True
						}
						db.updateUser({"Email": values["email"]}, newValues, values["password"])
						break

					elif o_event == "update":
						overlayed.close()
						overlayed = Window(winName, updateLayout, modal=True)
						continue

					elif o_event == "o_back":
						o_layout = [
							[Text("Do your bill is past due. Would you like to pay it now")],
							[Button("Yes, pay now", key="pay"), Button("No", "no_pay"), Button("Update payment info", key="update")]
						]
						overlayed.close()
						overlayed = Window(winName, o_layout, modal=True)
						continue
					
					elif o_event == "o_submit":
						o_values["email"] = userData["email"]
						code: tuple[bool, str] = _collectPayment(o_values, True)

						if code[0]:
							updatedData = {
								"Credit Card Number": o_values["ccn"],
								"Code": o_values["code"],
								"State": o_values["state"],
								"City": o_values["city"],
								"Address": o_values["addy"],
								"Zip": o_values["zip"],
								"First Name": o_values["fName"],
								"Last Name": o_values["lName"],
								"Exp date": o_values["exp"],
								"Was Last Payment Recieved": True,
								"Pay day": _getNextMonth()
							}
							db.updateUser({"Email": values["email"]}, updatedData, values["password"])
							overlayed.close()
							break

						updateLayout.append([Text(code[1], text_color="red")])
						overlayed.close()
						overlayed = Window(winName, updateLayout, modal=True)
						del updateLayout[-1]
						continue

			attemptLogin(values["email"], userData["Password"], values["mfa"])
			if userAuth.isLoggedIn == False:
				login.close()
				layout.append([Text(userAuth.loginInfo, text_color="red")])
				login = Window(winName, layout)

		elif event == "back":
			login.close()
			return True

	db.close()
	login.close()
	return False

def _isEmpty(values) -> bool:
	'''
	Check if any value in values is empty

	# Params:
	values - All text field values

	# Returns:
	True if one or more text fields are empty
	'''
	if values["email"] == "":
		return True

	if values["password"] == "":
		return True

	if values["ccn"] == "":
		return True

	if values["code"] == "":
		return True

	if values["state"] == "":
		return True

	if values["city"] == "":
		return True

	if values["addy"] == "":
		return True

	if values["zip"] == "":
		return True

	if values["exp"] == "":
		return True

	if values["fName"] == "":
		return True

	if values["lName"] == "":
		return True

	return False

def _stripValues(values):
	values["email"] = values["email"].strip()
	values["mfa"] = values["mfa"].strip()
	values["ccn"] = values["ccn"].strip()
	values["code"] = values["code"].strip()
	values["state"] = values["state"].strip()
	values["city"] = values["city"].strip()
	values["addy"] = values["addy"].strip()
	values["zip"] = values["zip"].strip()
	values["exp"] = values["exp"].strip()
	values["fName"] = values["fName"].strip()
	values["lName"] = values["lName"].strip()

	return values

def signUpScreen() -> bool:
	'''
	# Returns:
	True if user has signed up successfuly. False if user clicks back button
	'''
	layout = [
		[Text("Enter your robinhood account email address:"), Input(key="email")],
		[Text("Create an account password:"), Input("", key="acc_password", password_char="*")],
		[Text("Enter your robinhood account password (must be different from account password):"), Input("", key="password",
			password_char="*")],
		[Text("Enter two factor authentication code. If one is not needed leave blank:"),
			Input(key="mfa")],
		[Text("Enter your credit card number:"), Input("", key="ccn")],
		[Text("Enter credit card code:"), Input("", key="code",
			password_char="*")],
		[Text("State:"), Input("", key="state")],
		[Text("City:"), Input("", key="city")],
		[Text("Address:"), Input("", key="addy")],
		[Text("Zip Code:"), Input("", key="zip")],
		[Text("First Name:"), Input("", key="fName")],
		[Text("Last Name:"), Input("", key="lName")],
		[Text("Expiration Date (YYYY-MM):"), Input("", key="exp")],

		[Button("Submit", key="submit"), Button("Back", key="back")]
	]
	SIZE: int = len(layout)
	signUp = Window(winName, layout)
	db = DataBase()

	while True:
		rmtree(join(expanduser("~"), ".tokens"), ignore_errors=True)
		event, values = signUp.read()

		if exitApp(event, signUp, True):
			exit(0)

		if event == "back":
			signUp.close()
			return True

		if len(layout) > SIZE:
			del layout[-1]

		try:
			checkConnection()
		except:
			layout.append([Text("Check your internet connection", text_color="red")])
			signUp.close()
			signUp = Window(winName, layout)
			continue

		values = _stripValues(values)

		if _isEmpty(values):
			layout.append([Text("All fields are required", text_color="red")])
			signUp.close()
			signUp = Window(winName, layout)
			continue

		if values["password"] == values["acc_password"]:
			layout.append([Text("Your robinhood account password cannot be the same as your Stockify account password", text_color="red")])
			signUp.close()
			signUp = Window(winName, layout)
			continue

		try:
			datetime.strptime(values["exp"], "%Y-%m")
		except:
			layout.append([Text("Please enter the expiration data in the proper format", text_color="red")])
			signUp.close()
			signUp = Window(winName, layout)
			continue

		attemptLogin(values["email"], values["password"], values["mfa"])
		if userAuth.isLoggedIn == False:
			layout.append([Text(f"Robinhood's servers said, \"{userAuth.loginInfo}\"", text_color="red")])
			signUp.close()
			signUp = Window(winName, layout)
			continue

		db.connect()

		try:
			if db.findUsers({"Email": values["email"]}) != []:
				layout.append([Text(("User %s already has an account", values["email"]), text_color="red")])
				signUp.close()
				signUp = Window(winName, layout)
				continue
		except:
			layout.append([Text("Check your internet connection", text_color="red")])
			signUp.close()
			signUp = Window(winName, layout)
			continue

		# test if credit card works
		code: tuple = _collectPayment(values, False)

		if code[0]:
			usr: dict = db.createUser(values["email"], values["password"], values["ccn"],
				values["code"], values["state"], values["city"], values["addy"],
				values["zip"], values["fName"], values["lName"], values["exp"],
				_getNextMonth(), code[0], False
			)
		else:
			layout.append([Text(code[1], text_color="red")])
			signUp.close()
			signUp = Window(winName, layout)
			continue

		try: # attempt to create account
			db.encrypt(usr, values["acc_password"])
		except:
			layout.append([Text("Check you internet connection", text_color="red")])
			signUp.close()
			signUp = Window(winName, layout)
			continue

		# charge credit card this time
		code: tuple = _collectPayment(values, True)

		if code[0] == False:
			layout.append([Text(code[1], text_color="red")])
			signUp.close()
			signUp = Window(winName, layout)
			continue

		db.close()
		signUp.close()
		return False