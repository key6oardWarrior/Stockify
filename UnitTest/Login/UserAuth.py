from sys import path, argv

path[0] = path[0][:path[0].rfind("\\")]
path[0] = path[0][:path[0].rfind("\\")]

from helper import _checkConnection, ConnectionError
from Login import UserAuth

class UnitTest(UserAuth):
	def __init__(self) -> None:
		pass

	def connectionTest(self) -> int:
		try:
			super().__init__()
		except ConnectionError as ce:
			print("Connection error occured:", ce)
			return 0

		return 1

	def testLogin(self) -> int:
		try:
			self.login()
			self.login()
		except:
			return 1
		
		return 0

	def testLogout(self) -> int:
		try:
			self.logout()
		except:
			return 1

		return 0

test = UnitTest()

# if testing with no internet connection or with internet connection
if argv[1] == "--no-connection":
	assert test.connectionTest() == 0
	assert test.testLogin() == 1
	assert test.testLogout() == 1
elif argv[1] == "--connected":
	assert test.connectionTest() == 1
	assert test.testLogin() == 0
	assert test.testLogout() == 0