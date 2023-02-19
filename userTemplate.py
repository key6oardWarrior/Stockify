from datetime import date, datetime
from getpass import getpass
from sys import path, platform

from Helper.Errors import (IncorrectPassword, UserAlreadyExist,
    UserAlreadyLoaded, UserDoesNotExist)
from Robinhood_API.Login import UserAuth
from ServerSide.DataBase import DataBase

if platform == "win32":
	slash = "\\"
else:
	slash = "/"

path.append(path[0][:path[0].rfind(slash)])

def getInt(MSG: str) -> int:
	while True:
		try:
			return int(input(MSG))
		except:
			print("Only enter numbers")

def getDates() -> tuple[datetime]:
	while True:
		exp = input("Enter data mm/dd/yyyy: ").strip()

		try:
			exp: datetime = datetime.strptime(exp, "%m/%d/%Y")
		except:
			print("Only enter numbers for date in given format")
			continue
		else:
			break

	today = datetime.strptime(date.today().isoformat(), "%Y-%m-%d")
	tmr = ""
	month = today.month
	year = today.year

	tmr += str(year) + "/" if month < 12 else str(year + 1)
	tmr += str(month + 1) + "/" if month < 12 else "1"
	tmr += str(today.day)

	return (exp, datetime.strptime(tmr, "%Y/%m/%d"))

def getPayment() -> bool: return True

auth = UserAuth()
dataBase = DataBase()
sign_up_or_in = input("Do you want to sign up (U) or sign in (I): ").strip().lower()
email, password = auth.login()

if sign_up_or_in == "u":
	ccn: int = getInt("Enter credit card number: ")
	addy: str = input("Enter addresses: ")
	cvv: int = getInt("Enter CVV: ")
	dates: tuple[datetime] = getDates()

	try:
		dataBase.addUser(dataBase.createUser(
			email,
			password,
			ccn,
			addy,
			cvv,
			dates[0],
			dates[1],
			getPayment(),
			False
		))
	except UserAlreadyExist as e:
		print(e)
else:
	try:
		dataBase.decrypt(email, password)
	except UserAlreadyLoaded as e:
		print(e)
	except UserDoesNotExist as e:
		print(e)
	except IncorrectPassword as e:
		if auth.isLoggedIn:
			print("The password is incorrrect, but Robinhood was successfully logged in. This means your robinhood password was changed.")
			ans = input("Enter Y to make a new Stockify account, or enter N to update your account").strip().lower()

			if ans == "y":
				dates: tuple[datetime] = getDates()
				dataBase.removeUser({"Email": email})
				dataBase.addUser(dataBase.createUser(
					email,
					getpass("Enter password: "),
					input("Enter credit card number: "),
					input("Enter addy: "),
					input("Enter cvv: "),
					dates[0],
					dates[1],
					True,
					False
				))
			else:
				oldPass = getpass("Enter old password: ")
				dataBase.decrypt(email, oldPass)
				dataBase.updateUser({email: oldPass}, {email: getpass("Enter new robinhood password: ")})

del password
dataBase.encrypt({"Emai": email})