from sys import exit
from os.path import expanduser, join
from shutil import rmtree

from Helper.Errors import ConnectionError
from Robinhood_API.Login import UserAuth

userAuth = UserAuth()

def checkConnection():
	from socket import create_connection

	try:
		create_connection(("1.1.1.1", 443)).close()
	except:
		raise ConnectionError("Cannot connect to the internet")

from decimal import Decimal
from authorizenet.apicontractsv1 import (ArrayOfLineItem, ArrayOfSetting,
createTransactionRequest, creditCardType, customerAddressType,
customerDataType, lineItemType, merchantAuthenticationType, orderType,
paymentType, settingType, transactionRequestType)
from authorizenet.apicontrollers import createTransactionController
from Helper.creds import apiLoginId, transactionKey

from PySimpleGUI.PySimpleGUI import WIN_CLOSED, Window

def getPayment(email: str, ccn: str, code: str, state: str, city: str,
	address: str, _zip: str, exp: str, fName: str, lName: str,
	isCharging: bool) -> tuple[bool, str]:
	'''
	Charge a credit card. Useful Authorize.Net docs can be found at:\n
	Responce Codes: https://developer.authorize.net/api/reference/features/errorandresponsecodes.html\n
	Hello World: https://developer.authorize.net/hello_world/testing_guide.html\n
	Code Docs: https://developer.authorize.net/api/reference/index.html

	# Params
	email - The user's email address\n
	cnn - Credit card number\n
	code - Credit card code\n
	state - US state\n
	city - the state's city\n
	addy - user's address\n
	_zip - users US zip coden\n
	exp - Credit card expiration date\n
	fName - First name\n
	lName - Last name\n
	isCharging - True if charging the credit card

	# Returns:
	A tuple containing if successful and the status code
	'''
	# Create a merchantAuthenticationType object with authentication details
	# retrieved from the constants file
	merchantAuth = merchantAuthenticationType()
	merchantAuth.name = apiLoginId
	merchantAuth.transactionKey = transactionKey

	# get card data from user
	creditCard = creditCardType()
	creditCard.cardNumber = ccn
	creditCard.expirationDate = exp
	creditCard.cardCode = code

	# get payment data
	payment = paymentType()
	payment.creditCard = creditCard

	# order info
	order = orderType()
	order.invoiceNumber = ""
	order.description = "Stockify's Monthly Service Fee"

	# address info
	addy = customerAddressType()
	addy.country = "USA"
	addy.email = email
	addy.state = state
	addy.city = city
	addy.address = address
	addy.zip = _zip
	addy.firstName = fName
	addy.lastName = lName

	# customer's identifying information
	customerData = customerDataType()
	customerData.type = "individual"
	customerData.id = ""
	customerData.email = email

	# Add values for transaction settings
	duplicateWindowSetting = settingType()
	duplicateWindowSetting.settingName = "duplicateWindow"
	duplicateWindowSetting.settingValue = "600"
	settings = ArrayOfSetting()
	settings.setting.append(duplicateWindowSetting)

	# the item the user is buying
	item = lineItemType()
	item.itemId = "00001"
	item.name = "Subscription"
	item.description = "Monthly subscription to Stockify"
	item.quantity = "1"
	item.unitPrice = "10.0"

	# transaction info
	transaction = transactionRequestType()
	if isCharging:
		transaction.transactionType = "authCaptureTransaction"
	else:
		transaction.transactionType = "authOnlyTransaction"
	transaction.amount = Decimal("10.0")
	transaction.payment = payment
	transaction.order = order
	transaction.billTo = addy
	transaction.customer = customerData
	transaction.transactionSettings = settings
	transaction.lineItems = ArrayOfLineItem().lineItem.append(item)

	request = createTransactionRequest()
	request.merchantAuthentication = merchantAuth
	request.refId = "MerchantID-0001"
	request.transactionRequest = transaction

	transactionController = createTransactionController(request)
	transactionController.execute()

	responce = transactionController.getresponse()

	# return true if success
	code: str = responce.messages.message.code.text
	return (True, code) if code == "I00001" else (False, code)

from robin_stocks.authentication import logout

def killApp() -> None:
	'''
	Exit app ASAP
	'''
	rmtree(join(expanduser("~"), ".tokens"), ignore_errors=True)

	if userAuth.isLoggedIn:
		logout()

	exit(0)

def exitApp(event, window: Window, isLogout=False) -> bool:
	'''
	Determin if the event wants app to die

	# Params:
	event - If the user clicked exit or clicked the exit at the top left of
	app\n
	window - The window to close\n
	isLogout - True if you want to logout of Robinhood

	# Returns:
	True if event = Exit or WIN_CLOSED (see PyGUI) else False
	'''
	if((event == "Exit") or (event == WIN_CLOSED)):
		window.close()

		if((isLogout) and (userAuth.isLoggedIn)):
			logout() # logout of user's robinhood account on close

		rmtree(join(expanduser("~"), ".tokens"), ignore_errors=True)
		return True
	return False