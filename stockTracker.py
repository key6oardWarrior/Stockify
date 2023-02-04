from Request import Request
from os.path import exists
from os import remove

request = Request()

# remove not needed log files
if exists("geckodriver.log"):
	remove("geckodriver.log")