from base64 import b64decode, b64encode
from datetime import datetime
from hashlib import sha256

from Cryptodome.Cipher.AES import MODE_CBC, block_size, new
from Cryptodome.Random import new as rand_new

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database

from Helper.creds import connectionString, certFile
from Helper.Errors import (IncorrectPassword, UserAlreadyExist,
    UserAlreadyLoaded, UserDoesNotExist)

class DataBase:
	__client: MongoClient
	__users_db: Database
	__usersCollections: Collection
	__userData = None

	def __init__(self) -> None:
		self.__client = MongoClient(connectionString, tls=True,
			tlsCertificateKeyFile=certFile)
		self.__users_db: Database = self.__client["Users"]
		self.__usersCollections = self.__users_db["PaymentData"]

	def createUser(self, email: str, password: str, ccn: str,
		code: str, state: str, city: str, addy: str, _zip: str, fName: str,
		lName: str, exp: datetime, pay_day: datetime, payment_received: bool,
		isEnc=True) -> dict:
		'''
		Set isEnc equal to False if password and code is plain text\n
		DB Key
		{
			"Email": str,
			"Password": str,
			"Credit Card Number": str,
			"Code": str,
			"State": str,
			"City": str,
			"Address": str,
			"Zip": str,
			"First Name": str,
			"Last Name": str,
			"Exp Date": datetime,
			"Pay date": datetime,
			"Was Last payment recieved": bool
		}
		'''

		if isEnc:
			return {
					"Email": email,
					"Password": password,
					"Credit Card Number": ccn,
					"Code": code,
					"State": state,
					"City": city,
					"Address": addy,
					"Zip": _zip,
					"First Name": fName,
					"Last Name": lName,
					"Exp date": exp,
					"Pay date": pay_day,
					"Was Last Payment Recieved": payment_received
				}

		# ensure the same user cannot be added twice
		if self.findUsers({"Email": email}) != []:
			raise UserAlreadyExist(f"User {email} already exists")

		return {
				"Email": email,
				"Password": sha256(password.encode()).hexdigest(),
				"Credit Card Number": ccn,
				"Code": sha256(code.encode()).hexdigest(),
				"State": state,
				"City": city,
				"Address": addy,
				"Zip": _zip,
				"First Name": fName,
				"Last Name": lName,
				"Exp date": exp,
				"Pay date": pay_day,
				"Was Last Payment Recieved": payment_received
			}

	def removeUser(self, query: dict[str, str or int or datetime or
		dict[str: str]]) -> None:
		'''
		Delete a user using a query search against the Collection object.
		Advanced and Regular expression query search are allowed

		# Params:
		query - The query that will be used to search the Collection for a user
		'''
		if self.findUsers(query) == []:
			raise UserDoesNotExist("The user is not in the database")

		if self.__userData == None:
			raise IncorrectPassword("User not decrypted")

		self.__usersCollections.delete_one(query)

	def updateUser(self, query: dict, newValue: tuple, isEnc=True) -> None:
		'''
		Update a user's data using query search and replace data with newValue.
		Advanced and Regular expression query search not allowed.

		# Params:
		query - The query that will be used to search the Collection for a user\n
		newValue - The new value(s) that will be put into the database\n
		isEnc (optional) - True If Password and Code are both hashed else False
		'''
		if ("Email" in newValue):
			if self.findUsers({"Email": newValue["Email"]}) != []:
				raise UserAlreadyExist("User already in database")

		if self.__userData != None:
			for itr in newValue:
				if((isEnc == False) and ((itr == "Password") or (itr == "Code"))):
					self.__userData[itr] = sha256(newValue[itr].encode()).hexdigest()
				else:
					self.__userData[itr] = newValue[itr]
		else:
			raise IncorrectPassword("User not decrypted")

		self.encrypt(self.__userData, True)
		self.removeUser(query)

	def findUsers(self, query: dict[str, str or int or datetime or 
		dict[str: str]], limit: int=0) -> list[Cursor]:
		'''
		Find a user using a query search against the Collection object.
		Advanced and Regular expression query search are allowed

		# Params:
		query - The query that will be used to search the Collection for a user\n
		limit (optional) - The max number of users to be returned. 0 = all users

		# Returns:
		The user(s) that have matched the query
		'''
		users = []
		for itr in self.__usersCollections.find(query).limit(limit):
			users.append(itr)

		return users

	def __pad(self, plain_text: str):
		'''
		Pad a string
		'''
		number_of_bytes_to_pad = block_size - len(plain_text) % block_size
		return plain_text + (number_of_bytes_to_pad * chr(number_of_bytes_to_pad))

	def encrypt(self, user: dict, isUpdate=False) -> None:
		'''
		All user data must be encrypted using AES-128-CBC to ensure security.
		Advanced and Regular expression query search are not allowed. This will
		remove the user from the DB. Before closing a user's connection encrypt
		their data.

		# Params:
		user - The dictionary that contains all user data and that data will be
		encrypted\n
		isUpdate (optional) - Do NOT set unless function is being called from
		updateUser method
		'''
		if isUpdate == False:
			if self.findUsers({"Email": user["Email"]}) != []:
				raise UserAlreadyExist("User already exist")

		# add user's strings to data
		data = ""
		itr = iter(user.keys())
		for ii in range(10):
			data += user[next(itr)] + "\n"

		# add remaining data
		key = next(itr)
		data += str(user[key].year) + "," + str(user[key].month) + "\n"

		key = next(itr)
		data += str(user[key].year) + "," + str(user[key].month) + "," + \
			str(user[key].day) + "\n"

		key = next(itr)
		data += str(user[key]) + "\n"
		data += "Test this string"

		# pad string
		data = self.__pad(data)

		# encrypt the user's data using AES-128-CBC
		iv = rand_new().read(block_size)
		cipher = new(bytearray.fromhex(user["Password"]), MODE_CBC, iv)
		encrypted = cipher.encrypt(data.encode())

		# store encrypted data
		document = {
			"Email": user["Email"],
			"Data": b64encode(iv + encrypted).decode("utf-8")
		}
		self.__usersCollections.insert_one(document)

	def decrypt(self, email: str, password: str) -> None:
		'''
		Decrypt the user's data.

		# Params:
		email - The user's data that needs to be loaded\n
		password - The user's password
		'''
		if self.__userData:
			raise UserAlreadyLoaded("Cannnot decrypt user twice")

		user: list[Cursor] = self.findUsers({"Email": email})
		if user == []:
			raise UserDoesNotExist("User is not in database")

		encrypted = b64decode(user[0]["Data"])
		iv = encrypted[:block_size]
		cipher = new(sha256(password.encode()).digest(), MODE_CBC, iv)

		try:
			plain_text = cipher.decrypt(encrypted[block_size:]).decode("utf-8")
		except:
			raise IncorrectPassword("The password entered was incorrect")

		plain_text: str = plain_text[:-ord(plain_text[len(plain_text) - 1:])]
		lst: list[str] = plain_text.split("\n")

		if lst[-1] != "Test this string":
			raise IncorrectPassword("The password entered was incorrect")

		date1_delim = lst[10].find(",")
		date2_delim = lst[11].find(",")
		rdate2_delim = lst[11].rfind(",")

		self.__userData = self.createUser(lst[0], lst[1], lst[2], lst[3], lst[4], lst[5],
			lst[6], lst[7], lst[8], lst[9],

			datetime(int(lst[10][:date1_delim]), int(lst[10][date1_delim+1:]), 1),

			datetime(int(lst[11][:date2_delim]), int(lst[11][date2_delim+1: rdate2_delim]),
			int(lst[11][rdate2_delim+1:])),
			
			bool(lst[12]))

	@property
	def userData(self) -> dict:
		return self.__userData