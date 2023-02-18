from os.path import exists
from os import remove
from datetime import datetime, date
from dateutil import relativedelta

from Robinhood_API.Login import UserAuth
from ServerSide.DataBase import DataBase, IncorrectPassword, UserAlreadyExist, \
	UserAlreadyLoaded, UserDoesNotExist
from getpass import getpass

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
	dataBase.decrypt(email, password)

del password
dataBase.encrypt({"Emai": email})