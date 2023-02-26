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

class TransactionFailed(BaseException):
	pass

class EncryptedUser(BaseException):
	pass