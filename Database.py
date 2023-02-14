from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.results import InsertOneResult
from datetime import datetime

class DataBase:
	__DB_LOCATION: str = "mongodb://localhost:27017/"
	__oneResults: dict[int: InsertOneResult] = {}
	__client: MongoClient
	__users_db: Database
	__usersCollections: Collection
	__size: int = 0 # number of users

	def __init__(self) -> None:
		self.__client = MongoClient(self.__DB_LOCATION)
		self.__users_db: Database = self.__client["Users"]
		self.__usersCollections = self.__users_db["PaymentData"]

	def createUser(self, email: str, ccn: int, addy: str, cvv: int,
		exp: datetime, pay_day: datetime, payment_received: bool) -> dict:
		'''
		DB Key
		{
			"Email": str,
			"Credit Card Number": int,
			"Address": str,
			"CVV": int,
			"Exp Date": datetime,
			"Pay date": datetime,
			"Was Last payment recieved": bool
		}
		'''
		return {
				"Email": email,
				"Credit Card Number": ccn,
				"Address": addy,
				"CVV": cvv,
				"Exp date": exp,
				"Pay date": pay_day,
				"Was Last Payment Recieved": payment_received
			}

	def addResult(self, user: dict) -> None:
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
		dict[str: str]]) -> list[dict]:
		'''
		Delete a user using a query search against the Collection object.
		Advanced and Regular expression query search are allowed

		# Params:
		query - The query that will be used to search the Collection for a user
		'''
		self.__usersCollections.delete_one(query)
		self.__size -= 1

	def updateUser(self, query: dict, newValue: dict) -> None:
		'''
		Update a user's data using query search and replace data with newValue

		# Params:
		query - The query that will be used to search the Collection for a user\n
		newValue - The new value(s) that will be put into the database
		'''
		self.__usersCollections.update_one(query, newValue)

	def findUser(self, query: dict[str, str or int or datetime or 
		dict[str: str]], limit: int=0) -> list[dict]:
		'''
		Find a user using a query search against the Collection object.
		Advanced and Regular expression query search are allowed

		# Params:
		query - The query that will be used to search the Collection for a user\n
		limit (optional) - The max number of users to be returned. 0 = all users
		'''
		users = []
		for itr in self.__usersCollections.find(query).limit(limit):
			users.append(itr)

		return users

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