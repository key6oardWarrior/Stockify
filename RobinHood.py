from robin_stocks.authentication import login, logout
from Request import ConnectionError
from getpass import getpass

def _checkConnection():
	from socket import create_connection

	try:
		create_connection(("1.1.1.1", 443)).close()
	except:
		raise ConnectionError("Cannot connect to the internet")

class UserAuth:
	__isLoggedIn = False
	__loginInfo = None

	def __init__(self) -> None:
		_checkConnection()

	def login(self) -> None:
		# don't login twice
		if self.__isLoggedIn:
			return

		print("Have your two factor authentication code ready if you have one\n")
		USER_NAME = input("Enter user name: ")
		PASSWORD = getpass("Enter password: ")
		MFA = input("Enter two factor authentication code. If one is not needed enter \"none\": ")

		# robin_stocks.authentication.login
		if MFA.strip().lower() == "none":
			self.__loginInfo = login(USER_NAME, PASSWORD)
		else:
			self.__loginInfo = login(USER_NAME, PASSWORD, mfa_code=MFA)

		self.__isLoggedIn = True

	def logout(self) -> None:
		if self.__isLoggedIn:
			logout()
			self.__isLoggedIn = False

	@property
	def isLoggedIn(self) -> bool:
		return self.__isLoggedIn

	@property
	def loginInfo(self) -> dict | None:
		if self.__isLoggedIn == False:
			return None
		return self.__loginInfo

class _UnitTest(UserAuth):
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

if __name__ == "__main__":
	unitTest = _UnitTest()
	assert unitTest.connectionTest() == 1
	assert unitTest.testLogin() == 0

	print(unitTest.loginInfo)
	unitTest.testLogout()