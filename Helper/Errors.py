class IncorrectPassword(BaseException):
	pass

class UserAlreadyExist(BaseException):
	pass

class UserAlreadyLoaded(BaseException):
	pass

class UserDoesNotExist(BaseException):
	pass

class ConnectionError(BaseException):
	pass