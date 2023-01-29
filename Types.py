from enum import Enum
from selenium import webdriver

class Types(Enum):
	Buy = 0,
	Sell = 1,
	Exchange = 2,
	Received = 3

def type_to_str(type_: Types) -> str:
	if type_ == Types.Buy:
		return "Buy"

	if type_ == Types.Sell:
		return "Sell"

	if type_ == Types.Exchange:
		return "Exchange"

	return "Received"

class Browser(Enum):
	FireFox = 0,
	Chrome = 1,
	Safari = 2

def pickBrowser(BROWSER: Browser):
	if BROWSER == Browser.FireFox:
		return webdriver.Firefox()

	if BROWSER == Browser.Chrome:
		return webdriver.Chrome()

	if BROWSER == Browser.Safari:
		return webdriver.Safari()

def setBrowser() -> Browser:
	try:
		webdriver.Firefox().close()
		return Browser.FireFox
	except:
		webdriver.Chrome().close()
		return Browser.Chrome
