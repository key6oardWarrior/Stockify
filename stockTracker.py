from os.path import exists
from os import remove
from Robinhood_API.Login import UserAuth

# remove not needed log files
if exists("geckodriver.log"):
	remove("geckodriver.log")