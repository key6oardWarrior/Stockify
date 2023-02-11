class ConnectionError(BaseException):
	pass

def _checkConnection():
	from socket import create_connection

	try:
		create_connection(("1.1.1.1", 443)).close()
	except:
		raise ConnectionError("Cannot connect to the internet")