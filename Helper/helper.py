from Helper.Errors import ConnectionError

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

def getPayment(email: str, ccn: str, code: str, state: str, city: str,
	address: str, _zip: str, exp: str, fName: str, lName: str) -> tuple[bool, str]:
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
	order.invoiceNumber = "00001"
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
	customerData.id = "99999456654"
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
	transaction.transactionType = "authCaptureTransaction"
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
