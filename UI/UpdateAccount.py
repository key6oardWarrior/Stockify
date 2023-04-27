from PyGUI import Window, Text, Button, Input
from Helper.creds import winName
from Helper.helper import exitApp, exit
from Helper.Errors import UserDoesNotExist, IncorrectPassword
from ServerSide.DataBase import DataBase

from datetime import datetime

def _isEmpty(values: dict[str, str]) -> bool:
	'''
	# Params:
	values - Ensure all values in map are not empty

	# Returns:
	True if all values are empty else False
	'''
	SIZE = len(values)
	cnt = 0

	for value in values.values():
		if value.strip() == "":
			cnt += 1

	return cnt == SIZE

def updateAccount() -> bool:
	layout = [
		[Text("Enter your robinhood email address:"), Input(key="email", size=(30, 1))],
		[Text("Enter your account password:"), Input(key="password", password_char="*",
			size=(15, 1), do_not_clear=False)],
		[Button("Submit"), Button("Back")]
	]

	oLayout = [
		[Text("Only enter fields that you want to change")],
		[Text("Enter new your robinhood account email address:"), Input(key="Email")],
		[Text("Enter a new account password:"), Input(key="acc_password", password_char="*")],
		[Text("Enter new your robinhood account password (must be different from account password):"), Input(key="Password",
			password_char="*")],
		[Text("Enter two factor authentication code. If one is not needed leave blank:"),
			Input(key="mfa")],
		[Text("Enter your credit card number:"), Input(key="Credit Card Number")],
		[Text("Enter credit card code:"), Input(key="Code",
			password_char="*")],
		[Text("State:"), Input(key="State")],
		[Text("City:"), Input(key="City")],
		[Text("Address:"), Input(key="Address")],
		[Text("Zip Code:"), Input(key="Zip")],
		[Text("First Name:"), Input(key="First Name")],
		[Text("Last Name:"), Input(key="Last Name")],
		[Text("Expiration Date (YYYY-MM):"), Input(key="Exp date")],

		[Button("Submit"), Button("Back"), Button("Delete Account", key="del", button_color="red")]
	]
	SIZE = len(layout)
	O_SIZE = len(oLayout)
	db = DataBase()

	while True:
		db.connect()
		updateAcc = Window(winName, layout)
		event, values = updateAcc.read()

		if exitApp(event, updateAcc):
			exit(0)

		if event == "Back":
			updateAcc.close()
			return True

		if len(layout) > SIZE:
			layout = layout[:-1]

		values["email"] = values["email"].strip()
		if((values["email"] == "") or (values["password"] == "")):
			layout.append([Text("Username and password are required", text_color="red")])
			updateAcc.close()
			continue

		if db.isConnected == False:
			layout.append([Text("Check you internet connection", text_color="red")])
			updateAcc.close()
			continue

		try:
			db.decrypt(values["email"], values["password"])
		except UserDoesNotExist:
			layout.append([Text("User, {}, not found. You many need to sign up".format(values["email"]), text_color="red")])
			updateAcc.close()
			continue
		except IncorrectPassword:
			layout.append([Text("The password entered was incorrect", text_color="red")])
			updateAcc.close()
			continue

		while True:
			win = Window(winName, oLayout, modal=True)
			oEvent, oValues = win.read()

			if((exitApp(oEvent, win)) or (oEvent == "Back")):
				win.close()
				updateAcc.close()
				db.logout()
				break

			if len(oLayout) > O_SIZE:
				oLayout = oLayout[:-1]

			if oEvent == "Submit":
				if _isEmpty(oValues):
					oLayout.append([Text("All values cannot be blank", text_color="red")])
					win.close()
					continue

				if oValues["Password"] == oValues["acc_password"]:
					if oValues["Password"] != "":
						oLayout.append([Text("Passwords cannot be the same", text_color="red")])
						win.close()
						continue

				if oValues["Exp date"] != "":
					try:
						datetime.strptime(oValues["Exp date"], "%Y-%m")
					except:
						oLayout.append([Text("Please enter the expiration data in the proper format", text_color="red")])
						win.close()
						continue

				newValues = dict({})
				for key, value in oValues.items():
					if((key == "Password") or (key == "acc_password")):
						if value != "":
							newValues[key] = value
					else:
						if value != "":
							newValues[key] = value.strip()

				if oValues["acc_password"] == "":
					try:
						db.updateUser({"Email": values["email"]}, newValues,
							values["password"])
					except:
						oLayout.append([Text("Check your internet connection", text_color="red")])
						win.close()
						continue
				else:
					try:
						db.updateUser({"Email": values["email"]}, newValues,
							oValues["acc_password"])
					except:
						oLayout.append([Text("Check your internet connection", text_color="red")])
						win.close()
						continue

			elif oEvent == "del":
				try:
					db.removeUser({"Email": values["email"]})
					db.close()
				except:
					oLayout.append([Text("Check your internet connection", text_color="red")])
					win.close()
					continue

			layout.append([Text("Accout changes were successful")])
			win.close()
			updateAcc.close()
			db.close()
			break
