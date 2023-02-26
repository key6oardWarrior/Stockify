from datetime import date, datetime
from getpass import getpass
from sys import path, platform
from os.path import exists

if platform == "win32":
	from os.path import expanduser

	dataDir = expanduser("~") + "\\AppData\\Local\\Stockify"
elif((platform == "linux") or (platform == "linux2")):
	dataDir = "/usr/local/Stockify"
else: # darwin
	dataDir = "/usr/local/bin/Stockify"

if exists(dataDir) == False:
	raise FileExistsError("The necessary app data does not exists. Please reinstall the app.")

path.append(dataDir)

# WON'T GO INTO PRODUCTION
if platform == "win32":
	slash = "\\"
else:
	slash = "/"

path.append(path[0][:path[0].rfind(slash)])
del slash
# WON'T GO INTO PRODUCTION ^

from Helper.Errors import (IncorrectPassword, UserAlreadyExist,
    UserAlreadyLoaded, UserDoesNotExist, TransactionFailed)
from Helper.helper import getPayment

from ServerSide.DataBase import DataBase

from Robinhood_API.Login import UserAuth
from Robinhood_API.Account import *
from TradeData.Request import Request

def getInt(MSG: str) -> str:
	num: int

	while True:
		try:
			num = int(input(MSG).strip())
		except:
			print("Only enter numbers")
		else:
			return str(num)

def getDates(exp: str) -> tuple[datetime, datetime]:
	while True:
		try:
			exp: datetime = datetime.strptime(exp, "%Y-%m")
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

auth = UserAuth()
dataBase = DataBase()
sign_up_or_in = input("Do you want to sign up (U) or sign in (I): ").strip().lower()
email, password = auth.login()

if sign_up_or_in == "u":
	ccn: str = getInt("Enter credit card number: ")
	code: str = getInt("Enter credit card code: ")
	state: str = input("Enter your US state: ").strip()
	city: str = input("Enter your city: ").strip()
	addy: str = input("Enter addresses: ").strip()
	_zip: str = input("Enter your zip code: ").strip()
	exp: str = input("Enter card expire data (YYYY-MM): ").strip()
	fName: str = input("Enter first name: ").strip()
	lName: str = input("Enter last name: ").strip()

	gotPayment: tuple[bool, str] = getPayment(
		email,
		ccn,
		code,
		state,
		city,
		addy,
		_zip,
		exp,
		fName,
		lName
	)

	if gotPayment[0] == False:
		raise TransactionFailed(f"Transaction failed with code {gotPayment[1]}")

	dates: tuple[datetime, datetime] = getDates(exp)

	try:
		dataBase.addUser(dataBase.createUser(
			email,
			password,
			ccn,
			code,
			state,
			city,
			addy,
			_zip,
			fName,
			lName,
			dates[0],
			dates[1],
			gotPayment[0],
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
					input("Enter credit card code: "),
					input("Enter state: "),
					input("Enter city: "),
					input("Enter addy: "),
					input("Enter zip: "),
					input("First name: "),
					input("Last name: "),
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
# dataBase.encrypt({"Emai": email})

# make request to get all trade data
tradeData = Request()

ans = input("Do you want the last 30 days of trade data (y), or more data (n): ").lower().strip()
if ans == "y":
	tradeData.download()
else:
	tradeData.downloadAll()

tradeData.load()
get_open_stock_positions()