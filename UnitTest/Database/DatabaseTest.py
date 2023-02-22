from sys import path, platform

slash = "\\"

if platform != "win32":
	slash = "/"

addedPath = path[0][:path[0].rfind(slash)]
path.append(addedPath[:addedPath.rfind(slash)])
del slash, addedPath

from ServerSide.DataBase import DataBase
from datetime import datetime
from hashlib import sha256

class UnitTest(DataBase):
	def __init__(self, ipAddr) -> None:
		'''
		Test if the DB can be initalized

		# Params
		ipAddr - ip address that the server should return
		'''
		super().__init__()
		assert self.client.HOST == ipAddr, f"host is not {ipAddr}"

	def addUsers(self) -> None:
		'''
		Ensure that users can be added to the data base and found once added.
		Also ensure that all users 
		'''
		self.addUser(self.createUser(
			"john_doe@example.com", "1234", "1234567890", "321", "MI", "Dearborn",
			"123 Addy Lane", "12341", "John", "Doe", datetime(2025, 3, 5),
			datetime(2023, 3, 16), True, False
		))

		user: dict = self.findUsers({"Email": "john_doe@example.com"})[0]

		assert user["Email"] == "john_doe@example.com", "user not added to DB"
		assert user["Password"] == sha256("1234".encode()).hexdigest(), "Passwords does not match"
		assert user["Credit Card Number"] == "1234567890", "CCN does not match"
		assert user["Code"] == sha256("321".encode()).hexdigest(), "CVV does not match"
		assert self.num_users == 1, "Wrong amt of users detected"

	def remove(self) -> None:
		'''
		Test removing users and that the correct amt of users is stored.
		'''
		query = {"Email": "john_doe@example.com"}
		self.removeUser(query)
		assert self.findUsers(query) == [], "User was not removed"
		assert self.num_users == 0, "Wrong amt of users detected"

	def encrypt(self) -> None:
		query = {"Email": "john_doe@example.com"}
		super().encrypt(query)

	def decrypt(self, password: str) -> None:
		super().decrypt("john_doe@example.com", password)

		user: dict = self.findUsers({"Email": "john_doe@example.com"})[0]

		assert user["Email"] == "john_doe@example.com", "user not added to DB"
		assert user["Password"] == sha256(password.encode()).hexdigest(), "Passwords does not match"
		assert user["Credit Card Number"] == "1234567890", "CCN does not match"
		assert user["Code"] == sha256("321".encode()).hexdigest(), "CVV does not match"
		assert self.num_users == 1, "Wrong amt of users detected"

	def update(self) -> None:
		query = {"Email": "john_doe@example.com"}
		super().updateUser(query, {"Password": "5678"})

if __name__ == "__main__":
	# this is a localhost test
	test = UnitTest("localhost")

	# test can add user to db
	test.addUsers()

	# attempt to add the same user more than once
	try:
		test.addUsers()
	except:
		pass

	# test can encrypt data
	test.encrypt()

	# test if we can remove users from empty db
	test.remove()

	# test can decrypt data
	test.decrypt("1234")

	test.update()

	# ensure can re-encrypt
	test.encrypt()

	# ensure can re-decrypt
	test.decrypt("5678")

	# ensure that decrypted user can be removed
	test.remove()

	print("Passed")