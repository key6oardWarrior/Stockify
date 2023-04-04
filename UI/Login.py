from PySimpleGUI.PySimpleGUI import Button, Input, Text, Window

from Helper.creds import winName
from Helper.helper import exitApp, exit, getPayment, checkConnection, userAuth
from ServerSide.DataBase import DataBase

from Helper.Errors import IncorrectPassword, UserAlreadyExist

from shutil import rmtree
from os.path import join, expanduser
from requests import get
from json import loads
from datetime import datetime
from hashlib import sha256

def _attemptLogin(email: str, password: str, mfa: str=None) -> None:
	if mfa == "":
		mfa = None
	userAuth.login(email, password, mfa)

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

	db = DataBase()

	login = Window(winName, layout, modal=True)
	SIZE = len(layout)

	while userAuth.isLoggedIn == False:
		rmtree(join(expanduser("~"), ".tokens"), ignore_errors=True)
		event, values = login.read()

		if exitApp(event, login):
			exit(0)

		if len(layout) > SIZE:
			del layout[-1]

		try:
			checkConnection()
		except:
			layout.append([Text("Check Internet Connection", text_color="red")])
			login = Window(winName, layout, modal=True)
			continue

		if db.isConnected == False:
			db.connect()

		if event == "submit":
			if((values["email"] == "") or (values["password"] == "")):
				layout.append([Text("Enter your email and password to login", text_color="red")])
				login.close()
				login = Window(winName, layout)
				continue

			if db.isConnected == False:
				login.close()
				layout.append([Text("Check Internet Connection", text_color="red")])
				login = Window(winName, layout, modal=True)
				continue

			try: # if internet goes out
				if db.findUsers({"Email": values["email"]}) == []:
					layout.append([Text("User {} not found. You many need to sign up".format(values["email"]), text_color="red")])
					login.close()
					login = Window(winName, layout)
					continue

				db.decrypt(values["email"], sha256(values["password"]).hexdigest())
				userData: dict = db.userData
				today: datetime = datetime.today()
			except:
				login.close()
				layout.append([Text("Check Internet Connection", text_color="red")])
				login = Window(winName, layout, modal=True)
				continue

			if((userData["Was Last Payment Recieved"] == False) or
				((userData["Pay date"].month <= today.month) and
				(userData["Pay date"].day >= today.day))):

				try:
					db.updateUser({"Email": values["email"]},
						{"Was Last Payment Recieved": False})
				except IncorrectPassword as ip:
					login.close()
					layout.append([Text(ip.args[0], text_color="red")])
					login = Window(winName, layout, modal=True)
					continue
				except UserAlreadyExist as uae:
					login.close()
					layout.append([Text(uae.args[0], text_color="red")])
					login = Window(winName, layout, modal=True)
					continue
				except:
					login.close()
					layout.append([Text("Check Internet Connection", text_color="red")])
					login = Window(winName, layout, modal=True)
					continue

				while True:
					o_layout = [
						[Text("Do your bill is past due. Would you like to pay it now")],
						[Button("Yes, pay now", key="pay"), Button("No", key="no_pay"), Button("Update payment info", key="update")]
					]

					overlayed = Window(winName, o_layout)
					o_event, o_values = overlayed.read()

					if o_event == "pay":
						try:
							code: tuple[bool, str] = getPayment(userData["Email"],
								userData["Credit Card Number"], userData["Code"], userData["State"],
								userData["City"], userData["Address"], userData["Zip"],
								userData["Exp date"], userData["First Name"], userData["Last Name"]
							)
						except Exception as e:
							o_layout.append([Text("Payment failed, try again", text_color="red")])
							overlayed.close()
							overlayed = Window(winName, layout, modal=True)
							continue

						if code[0] == False:
							try:
								# get all of Authorize.Net's responce codes and display error message
								responceCodes = loads(get("https://developer.authorize.net/api/reference/dist/json/responseCodes.json").text)
							except:
								o_layout.append([Text("Payment failed, try again", text_color="red")])
								overlayed.close()
								overlayed = Window(winName, o_layout)
								continue

							for rc in responceCodes:
								if code[1] == rc["code"]:
									o_layout.append([Text(rc["text"], text_color="red")])
									overlayed.close()
									overlayed = Window(winName, o_layout)
									break

							continue

						overlayed.close()
						break

					elif o_event == "update":
						overlayed.close()
						overlayed = Window(winName, [
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
						])
						continue

					elif o_event == "o_back":
						o_layout = [
							[Text("Do your bill is past due. Would you like to pay it now")],
							[Button("Yes, pay now", key="pay"), Button("No", "no_pay"), Button("Update payment info", key="update")]
						]
						overlayed.close()
						overlayed = Window(winName, o_layout)
						continue
					
					elif o_event == "o_submit":
						try:
							code: tuple[bool, str] = getPayment(userData["email"], o_values["ccn"], o_values["code"],
								o_values["state"], o_values["city"], o_values["addy"], o_values["zip"],
								o_values["exp"], o_values["fName"], o_values["lName"])
						except Exception as e:
							o_layout.append([Text("There was an issue with payment proccessing. Please try again", text_color="red")])
							overlayed.close()
							overlayed = Window(winName, o_layout, modal=True)
							continue

						if code[0] == False:
							try:
								# get all of Authorize.Net's responce codes and display error message
								responceCodes = loads(get("https://developer.authorize.net/api/reference/dist/json/responseCodes.json").text)
							except:
								overlayed.Rows[0].append([Text("Reason login failed not given. Check internet connection.", text_color="red")])
								tempLayout = overlayed.Rows[0]
								overlayed.close()

								overlayed = Window(winName, tempLayout, modal=True)
								del tempLayout
								continue

							for rc in responceCodes:
								if code[1] == rc["code"]:
									overlayed.Rows[0].append([Text(rc["text"], text_color="red")])
									tempLayout = overlayed.Rows[0]
									overlayed.close()

									overlayed = Window(winName, tempLayout, modal=True)
									del tempLayout
									break

							continue

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
							"Was Last Payment Recieved": True
						}
						db.updateUser({"Email": values["email"]}, updatedData, False)
						overlayed.close()
						break

			_attemptLogin(values["email"].strip(), userData["Password"], values["mfa"].strip())
			if userAuth.isLoggedIn == False:
				login.close()
				layout.append([Text(userAuth.loginInfo, text_color="red")])
				login = Window(winName, layout, modal=True)

		elif event == "back":
			login.close()
			return True

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
	signUp = Window(winName, layout, modal=True)

	while True:
		event, values = signUp.read()

		if exitApp(event, signUp):
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
			signUp = Window(winName, layout, modal=True)
			continue

		values = _stripValues(values)

		if _isEmpty(values):
			layout.append([Text("All fields are required", text_color="red")])
			signUp.close()
			signUp = Window(winName, layout, modal=True)
			continue

		if values["password"] == values["acc_password"]:
			layout.append([Text("Your robinhood account password cannot be the same as your Stockify account password", text_color="red")])
			signUp.close()
			signUp = Window(winName, layout, modal=True)
			continue

		try:
			datetime.strptime(values["exp"], "%Y-%m")
		except:
			layout.append([Text("Please enter the expiration data in the proper format", text_color="red")])
			signUp.close()
			signUp = Window(winName, layout, modal=True)
			continue

		_attemptLogin(values["email"].strip(), values["password"], values["mfa"].strip())
		if userAuth.isLoggedIn == False:
			layout.append([Text(f"Robinhood's servers said, \"{userAuth.loginInfo}\"", text_color="red")])
			signUp.close()
			signUp = Window(winName, layout, modal=True)
			continue

		try:
			code: tuple[bool, str] = getPayment(values["email"], values["ccn"], values["code"],
				values["state"], values["city"], values["addy"], values["zip"],
				values["exp"], values["fName"], values["lName"])
		except Exception as e:
			layout.append([Text("Payment failed please try again", text_color="red")])
			signUp.close()
			signUp = Window(winName, layout, modal=True)
			continue

		# get all of Authorize.Net's responce codes and display error message
		if code[0] == False:
			try:
				responceCodes = loads(get("https://developer.authorize.net/api/reference/dist/json/responseCodes.json").text)
			except:
				layout.append([Text("Payment failed please try again", text_color="red")])
				signUp.close()
				signUp = Window(winName, layout, modal=True)
				continue

			for rc in responceCodes:
				if code[1] == rc["code"]:
					layout.append([Text(rc["text"], text_color="red")])
					signUp.close()
					signUp = Window(winName, layout, modal=True)
					break
			continue

		db = DataBase()
		usr = db.createUser(values["email"], values["password"], values["cnn"],
			values["code"], values["state"], values["city"], values["addy"],
			values["zip"], values["fName"], values["lName"], values["exp"],
			datetime.today(), True, False
		)

		db.encrypt(usr, values["acc_password"])
		break

	return False