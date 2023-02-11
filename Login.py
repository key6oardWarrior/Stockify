from getpass import getpass
from robin_stocks.authentication import login, logout
from helper import checkConnection

class UserAuth:
	__isLoggedIn = False
	__loginInfo = None

	def __init__(self) -> None:
		checkConnection()

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