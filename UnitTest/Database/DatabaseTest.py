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
	def __init__(self) -> None:
		'''
		Test if the DB can be initalized

		# Params
		ipAddr - ip address that the server should return
		'''
		super().__init__()

	def addUser(self) -> None:
		'''
		Ensure that users can be added to the data base and found once added.
		Also ensure that all users 
		'''
		user = self.createUser(
			"john_doe@example.com", "1234", "1234567890", "321", "MI", "Dearborn",
			"123 Addy Lane", "12341", "John", "Doe", "2027-05",
			datetime(2023, 3, 16), True, False)

		# ensure findUsers works
		assert super().findUsers({"Email": user["Email"]}) == [], "findUsers failed"

		assert user["Email"] == sha256("john_doe@example.com".encode()).hexdigest(), "user not added to DB"
		assert user["Password"] == "1234", "Passwords does not match"
		assert user["Credit Card Number"] == "1234567890", "CCN does not match"
		assert user["Code"] == sha256("321".encode()).hexdigest(), "CVV does not match"

		super().encrypt(user, "5678")

	def remove(self) -> None:
		'''
		Test removing users and that the correct amt of users is stored.
		'''
		query = {"Email": "jane_doe@example.com"}
		self.removeUser(query)
		assert self.findUsers(query) == [], "User was not removed"

	def decrypt(self, password: str) -> None:
		super().decrypt("john_doe@example.com", password)
		user = self.userData

		assert user["Email"] == sha256("john_doe@example.com".encode()).hexdigest(), "user not added to DB"
		assert user["Password"] == "1234", "Passwords does not match"
		assert user["Credit Card Number"] == "1234567890", "CCN does not match"
		assert user["Code"] == sha256("321".encode()).hexdigest(), "CVV does not match"

	def update(self) -> None:
		query = {"Email": "john_doe@example.com"}
		newValue = {
			"Email": "jane_doe@example.com",
			"Password": "5677848",
			"Was Last Payment Recieved": False
		}
		super().updateUser(query, newValue, "5678")

if __name__ == "__main__":
	test = UnitTest()

	# test can add user to db
	test.addUser()

	# attempt to add the same user more than once
	try:
		test.addUser()
	except:
		pass

	# test can decrypt data
	test.decrypt("5678")

	test.update()

	# ensure that decrypted user can be removed
	test.remove()

	print("Passed")