from datetime import datetime
from os.path import join, exists

from base64 import b64decode, b64encode
from hashlib import sha256
from Cryptodome.Cipher.AES import MODE_CBC, block_size, new
from Cryptodome.Random import new as rand_new

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database
from pymongo.results import InsertOneResult

class IncorrectPassword(BaseException):
	pass

class DataBase:
	__DB_LOCATION: str = "mongodb://localhost:27017/"
	__oneResults: dict[int: InsertOneResult] = {}
	__client: MongoClient
	__users_db: Database
	__usersCollections: Collection
	__size: int = 0 # number of users
	__PATH: str = "UserData"

	def __init__(self) -> None:
		self.__client = MongoClient(self.__DB_LOCATION)
		self.__users_db: Database = self.__client["Users"]
		self.__usersCollections = self.__users_db["PaymentData"]

		from os import mkdir
		from os.path import exists
		if exists(self.__PATH) == False:
			mkdir(self.__PATH)

	def createUser(self, email: str, password: str, ccn: int, addy: str,
		cvv: int, exp: datetime, pay_day: datetime,
		payment_received: bool, isEnc=True) -> dict:
		'''
		Set isEnc equal to False if password is plain text

		DB Key
		{
			"Email": str,
			"Password": str,
			"Credit Card Number": int,
			"Address": str,
			"CVV": int,
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
					"Address": addy,
					"CVV": str(cvv),
					"Exp date": exp,
					"Pay date": pay_day,
					"Was Last Payment Recieved": payment_received
				}

		return {
				"Email": email,
				"Password": sha256(password.encode()).hexdigest(),
				"Credit Card Number": ccn,
				"Address": addy,
				"CVV": sha256(str(cvv).encode()).hexdigest(),
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
			return

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

		if self.findUsers(query) == []:
			return

		self.__usersCollections.update_one(query, newValue)

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

	def encrypt(self, query) -> None:
		'''
		Store user data in secondary memory. All user data must be encrypted
		using AES-256-CBC to ensure security. Advanced and Regular expression
		query search are allowed. This will remove the user from the DB

		# Params:
		query - The query that will be used to search the Collection for a user
		'''
		if self.__size == 0:
			return

		if self.findUsers(query) == []:
			return

		user: Cursor = self.findUsers(query)[0]
		fileData =""

		# store all the user's data as a string
		for itr in user:
			if type(user[itr]) == str:
				fileData += user[itr]
			elif type(user[itr]) == datetime:
				fileData += str(user[itr].year) + "," + str(user[itr].month) + \
					"," + str(user[itr].day)
			elif((type(user[itr]) == int) or (type(user[itr]) == bool)):
				fileData += str(user[itr])
			else:
				continue

			fileData += "\n"

		# pad string
		fileData += "Test this string"
		fileData = self.__pad(fileData)

		# encrypt the user's data using AES-128-CBC
		iv = rand_new().read(block_size)
		cipher = new(user["Password"], MODE_CBC, iv)
		encrypted = cipher.encrypt(fileData.encode())

		# store encrypted data
		open(join(self.__PATH, user["Email"] + ".txt"), "w").write(
			b64encode(iv + encrypted).decode("utf-8"))

		self.removeUser(query)

	def decrypt(self, email: str, password: str) -> None:
		'''
		Decrypt a file that contains email's data then load that data. This
		will add a user to the DB

		# Params:
		email - The user's data that needs to be loaded
		password - The user's password
		'''
		if exists(join(self.__PATH, email + ".txt")) == False:
			return

		encrypted = b64decode(open(join(self.__PATH, email + ".txt"), "r").read())
		iv = encrypted[:block_size]
		cipher = new(sha256(password), MODE_CBC, iv)
		plain_text = cipher.decrypt(encrypted[block_size:]).decode("utf-8")
		plain_text: str = plain_text[:-ord(plain_text[len(plain_text) - 1:])]

		lst: list[str] = plain_text.split("\n")

		if lst[-1] != "Test this string":
			raise IncorrectPassword("The password entered was incorrect")

		date1_delim = lst[5].find(",")
		rdate1_delim = lst[5].rfind(",")
		date2_delim = lst[6].find(",")
		rdate2_delim = lst[6].rfind(",")

		user = self.createUser(lst[0], lst[1], int(lst[2]), lst[3], lst[4],
			datetime(int(lst[5][:date1_delim]), int(lst[5][date1_delim+1: rdate1_delim]),
			int(lst[5][rdate1_delim+1:])),

			datetime(int(lst[6][:date2_delim]), int(lst[6][date2_delim+1: rdate2_delim]),
			int(lst[6][rdate2_delim+1:])), bool(lst[7]))

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
