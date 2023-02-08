from Request import Request, exists
from os import remove

request = Request()

# remove not needed log files
if exists("geckodriver.log"):
	remove("geckodriver.log")