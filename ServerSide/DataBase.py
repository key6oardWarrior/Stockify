from base64 import b64decode, b64encode
from datetime import datetime
from hashlib import sha256

from Cryptodome.Cipher._mode_gcm import GcmMode
from Cryptodome.Cipher.AES import MODE_GCM, block_size, new
from Cryptodome.Protocol.KDF import scrypt
from os import urandom

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
	__isConnected = False

	def __init__(self) -> None:
		self.connect()

	def connect(self) -> None:
		'''
		Connect to the database
		'''
		# cant connect twice
		if self.__isConnected == False:
			try:
				self.__client = MongoClient(connectionString, tls=True)
				self.__users_db: Database = self.__client["Users"]
				self.__usersCollections = self.__users_db["PaymentData"]
			except:
				pass
			else:
				self.__isConnected = True

	def close(self) -> None:
		'''
		Close connection between client and server
		'''
		if self.__isConnected:
			self.__client.close()
			self.__isConnected = False
			del self.__userData
			self.__userData = None

	def createUser(self, email: str, password: str, ccn: str,
		code: str, state: str, city: str, addy: str, _zip: str, fName: str,
		lName: str, exp: str, pay_day: datetime, payment_received: bool,
		isEnc=True) -> dict:
		'''
		Set isEnc equal to False if code and email is plain text\n
		DB Map legend:
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
			"Exp Date": str,
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

		return {
				"Email": sha256(email.encode()).hexdigest(),
				"Password": password,
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

	def removeUser(self, query: dict[str, str], isEnc=False) -> None:
		'''
		Delete a user using a query search against the Collection object.
		Advanced and Regular expression query search are allowed

		# Params:
		query - Query that will be used to search the Collection for a user\n
		isEnc (optional) - If the email in query is hashed or not
		'''
		if "Email" not in query:
			raise ValueError("Cannot complete query")

		if isEnc == False:
			query["Email"] = sha256(query["Email"].encode()).hexdigest()

		if self.__findUsers(query) == []:
			raise UserDoesNotExist("The user is not in the database")

		if self.__userData == None:
			raise IncorrectPassword("User not decrypted")

		self.__usersCollections.delete_one(query)
		del self.__userData
		self.__userData = None

	def updateUser(self, query: dict[str, str], newValue: dict[str, str],
		password: str) -> None:
		'''
		Update a user's data using query search and replace data with newValue.
		Advanced and Regular expression query search not allowed.

		# Params:
		query - The query that will be used to search the Collection for a user\n
		newValue - The new value(s) that will be put into the database\n
		password - The password used to encrypt the data
		'''
		if "Email" not in query:
			raise ValueError("Cannot complete query")

		if "Email" in newValue:
			newValue["Email"] = sha256(newValue["Email"].encode()).hexdigest()
			if self.__findUsers({"Email": newValue["Email"]}) != []:
				raise UserAlreadyExist("User already in database")

		query["Email"] = sha256(query["Email"].encode()).hexdigest()
		if self.__userData:
			for itr in newValue:
				if(itr == "Code"):
					self.__userData[itr] = sha256(newValue[itr].encode()) \
						.hexdigest()
				else:
					self.__userData[itr] = newValue[itr]
		else:
			raise IncorrectPassword("User not decrypted")

		self.removeUser(query, True)
		self.encrypt(self.__userData, password, True)

	def findUsers(self, query: dict[str, str], limit: int=0) -> list[Cursor]:
		'''
		Find a user using a query search against the Collection object.
		Advanced and Regular expression query search are allowed

		# Params:
		query - The query that will be used to search the Collection for a user\n
		limit (optional) - The max number of users to be returned. 0 = all users\n

		# Returns:
		The user(s) that have matched the query
		'''
		if "Email" in query:
			query["Email"] = sha256(query["Email"].encode()).hexdigest()
		else:
			raise UserDoesNotExist("Email not in query")

		users = []
		for itr in self.__usersCollections.find(query).limit(limit):
			users.append(itr)

		return users

	def __findUsers(self, query: dict[str, str], limit: int=0) -> list[Cursor]:
		'''
		Find a user using a query search against the Collection object.
		Advanced and Regular expression query search are allowed

		# Params:
		query - The query that will be used to search the Collection for a user\n
		limit (optional) - The max number of users to be returned. 0 = all users\n

		# Returns:
		The user(s) that have matched the query
		'''
		users = []
		for itr in self.__usersCollections.find(query).limit(limit):
			users.append(itr)

		return users

	def encrypt(self, user: dict, password: str, isUpdate=False) -> None:
		'''
		All user data must be encrypted using AES-128-CBC to ensure security.
		Advanced and Regular expression query search are not allowed. This will
		remove the user from the DB. Before closing a user's connection encrypt
		their data.

		# Params:
		user - The dictionary that contains all user data and that data will be
		encrypted\n
		password - The password to encrypt the data\n
		isUpdate (optional) - Do NOT set unless function is being called from
		updateUser method
		'''
		if isUpdate == False:
			if self.__findUsers({"Email": user["Email"]}) != []:
				raise UserAlreadyExist("User already exist")

		# add user's strings to data
		data = ""
		itr = iter(user.keys())
		for ii in range(10):
			data += user[next(itr)] + "\n"

		# add remaining data
		key = next(itr)
		IDX = user[key].find("-")
		data += user[key][:IDX] + "," + user[key][IDX:] + "\n"

		key = next(itr)
		data += str(user[key].year) + "," + str(user[key].month) + "," + \
			str(user[key].day) + "\n"

		key = next(itr)
		data += str(user[key]) + "\n"
		data += "Test this string"

		# create cryptographically secure random numbers
		NONCE = urandom(12)
		SALT = urandom(block_size)

		# derive 32 byte key
		key = scrypt(password.encode(), SALT, key_len=32, N=16384, r=8, p=1)

		# AES-256-GCM algorithm
		cipher: GcmMode = new(key, MODE_GCM, nonce=NONCE)

		# encrypt
		ciphertext, tag = cipher.encrypt_and_digest(data.encode())

		# store encrypted data
		document = {
			"Email": user["Email"],
			"Data": b64encode(NONCE + SALT + ciphertext + tag).decode('utf-8')
		}
		self.__usersCollections.insert_one(document)

	def decrypt(self, email: str, password: str) -> None:
		'''
		Decrypt the user's data.

		# Params:
		email - The user's data that needs to be loaded\n
		password - The user's password
		'''
		email = sha256(email.encode()).hexdigest()
		if self.__userData:
			raise UserAlreadyLoaded("Cannnot decrypt user twice")

		user: list[Cursor] = self.__findUsers({"Email": email})
		if user == []:
			raise UserDoesNotExist("User is not in database")

		decoded = b64decode(user[0]["Data"])

		# get useful components
		NONCE = decoded[:12]
		SALT = decoded[12:28]
		ciphertext = decoded[28:-16]
		tag = decoded[-16:]

		# derive the key from the password
		key = scrypt(password.encode(), salt=SALT, key_len=32, N=16384, r=8, p=1)

		# decrypt
		cipher = new(key, MODE_GCM, nonce=NONCE)
		try:
			plain_text = cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
		except:
			raise IncorrectPassword("The password entered was incorrect")

		lst: list[str] = plain_text.split("\n")

		if lst[-1] != "Test this string":
			raise IncorrectPassword("The password entered was incorrect")

		date1_delim = lst[10].find(",")
		date2_delim = lst[11].find(",")
		rdate2_delim = lst[11].rfind(",")
		lst[12] = True if lst[12] == "True" else False

		self.__userData = self.createUser(lst[0], lst[1], lst[2], lst[3], lst[4], lst[5],
			lst[6], lst[7], lst[8], lst[9],

			(lst[10][:date1_delim] + lst[10][date1_delim+1:]),

			datetime(int(lst[11][:date2_delim]), int(lst[11][date2_delim+1: rdate2_delim]),
			int(lst[11][rdate2_delim+1:])), lst[12])

	def logout(self) -> None:
		'''
		Delete all of the user's decrypted data
		'''
		del self.__userData
		self.__userData = None

	@property
	def userData(self) -> dict:
		return self.__userData

	@property
	def isConnected(self) -> bool:
		return self.__isConnected