from base64 import b64decode, b64encode
from datetime import datetime
from hashlib import sha256

from Cryptodome.Cipher.AES import MODE_CBC, block_size, new
from Cryptodome.Random import new as rand_new

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database
from pymongo.results import InsertOneResult

from Helper.creds import connectionString
from Helper.Errors import (EncryptedUser, IncorrectPassword, UserAlreadyExist,
    UserAlreadyLoaded, UserDoesNotExist)

class DataBase:
	__oneResults: dict[int: InsertOneResult] = {}
	__client: MongoClient
	__users_db: Database
	__usersCollections: Collection
	__size: int # number of unencrypted users

	def __init__(self) -> None:
		self.__client = MongoClient(connectionString)
		self.__users_db: Database = self.__client["Users"]
		self.__usersCollections = self.__users_db["PaymentData"]
		self.__size = len(self.all_users)

	def createUser(self, email: str, password: str, ccn: str,
		code: str, state: str, city: str, addy: str, _zip: str, fName: str,
		lName: str, exp: datetime, pay_day: datetime, payment_received: bool,
		isEnc=True) -> dict:
		'''
		Set isEnc equal to False if password is plain text

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

		# ensure the same user cannot be added twice
		if self.findUsers({"Email": email}) != []:
			raise UserAlreadyExist(f"User {email} already exists")

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

	def addUser(self, user: dict) -> None:
		'''
		Add InsertOneResult to dict. Calling insert_one will return an
		InsertOneResults object. The object contains the _id for a user in the
		database.

		# Params:
		user - dict created by createUser
		'''
		self.__size += 1
		self.__oneResults[self.__size] = \
			self.__usersCollections.insert_one(user)

	def removeUser(self, query: dict[str, str or int or datetime or
		dict[str: str]]) -> None:
		'''
		Delete a user using a query search against the Collection object.
		Advanced and Regular expression query search are allowed

		# Params:
		query - The query that will be used to search the Collection for a user
		'''
		if self.__size == 0:
			return

		if self.findUsers(query) == []:
			raise UserDoesNotExist("The user is not in the database")

		self.__usersCollections.delete_one(query)
		self.__size -= 1

	def updateUser(self, query: dict, newValue: dict) -> None:
		'''
		Update a user's data using query search and replace data with newValue.
		Advanced and Regular expression query search are allowed

		# Params:
		query - The query that will be used to search the Collection for a user\n
		newValue - The new value(s) that will be put into the database
		'''
		if self.__size == 0:
			return

		user: list[Cursor] = self.findUsers(query)
		if user == []:
			raise UserDoesNotExist("The user is not in the database")
		elif ("Data" in user[0]):
			raise EncryptedUser("User is encrypted")

		if(("Password" in newValue) or ("CVV" in newValue)):
			itr = iter(newValue.keys())
			KEY: str = next(itr)
			newValue[KEY] = sha256(newValue[KEY].encode()).hexdigest()

		self.__usersCollections.update_one(query, {"$set": newValue})

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

	def __addEncryptedUser(self, user: dict[str, str]) -> None:
		self.__usersCollections.insert_one(user)
		self.__size += 1

	def encrypt(self, query: dict) -> None:
		'''
		Store user data in secondary memory. All user data must be encrypted
		using AES-128-CBC to ensure security. Advanced and Regular expression
		query search are allowed. This will remove the user from the DB. Before
		closing a user's connection encrypt their data.

		# Params:
		query - The query that will be used to search the Collection for a user
		'''
		if self.__size == 0:
			return

		user: list[Cursor] = self.findUsers(query)

		if user == []:
			return

		user: Cursor = user[0]

		# user already encrypted
		if ("Data" in user):
			return

		fileData = ""
		itr = iter(user)
		next(itr)
		key: str = next(itr)

		cnt = 0

		# add user's strings to fileData
		while cnt < 10:
			cnt += 1
			fileData += user[key] + "\n"
			key = next(itr)

		# add remaining data
		fileData += str(user[key].year) + "," + str(user[key].month) + "\n"

		key = next(itr)
		fileData += str(user[key].year) + "," + str(user[key].month) + "," + \
			str(user[key].day) + "\n"

		key = next(itr)
		fileData += str(user[key]) + "\n"
		fileData += "Test this string"

		# pad string
		fileData = self.__pad(fileData)

		# encrypt the user's data using AES-128-CBC
		iv = rand_new().read(block_size)
		cipher = new(bytearray.fromhex(user["Password"]), MODE_CBC, iv)
		encrypted = cipher.encrypt(fileData.encode())

		# store encrypted data
		self.removeUser(query)
		query["Data"] = b64encode(iv + encrypted).decode("utf-8")
		self.__addEncryptedUser(query)

	def decrypt(self, email: str, password: str) -> None:
		'''
		Decrypt a file that contains email's data then load that data. This
		will add a user to the DB

		# Params:
		email - The user's data that needs to be loaded\n
		password - The user's password
		'''
		if self.__size == 0:
			raise UserDoesNotExist("User is not in database")

		user: list[Cursor] = self.findUsers({"Email": email})
		if user == []:
			raise UserDoesNotExist("User is not in database")

		if ("Data" in user[0]) == False:
			raise UserAlreadyLoaded("User is already decrypted")

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

		self.removeUser({"Email": email})
		user = self.createUser(lst[0], lst[1], lst[2], lst[3], lst[4], lst[5],
			lst[6], lst[7], lst[8], lst[9],

			datetime(int(lst[10][:date1_delim]), int(lst[10][date1_delim+1:]), 1),

			datetime(int(lst[11][:date2_delim]), int(lst[11][date2_delim+1: rdate2_delim]),
			int(lst[11][rdate2_delim+1:])),
			
			bool(lst[12]))

		self.addUser(user)

	@property
	def _ids(self) -> dict:
		return self.__oneResults.values()

	@property
	def client(self) -> MongoClient:
		return self.__client

	@property
	def users_db(self) -> Database:
		return self.__users_db

	@property
	def userCollections(self) -> Collection:
		return self.__usersCollections

	@property
	def num_users(self) -> int:
		return self.__size

	@property
	def all_users(self) -> list[dict]:
		users = []
		for itr in self.__usersCollections.find():
			users.append(itr)

		return users
