from bs4 import BeautifulSoup
from requests import get
from wget import download
from numpy import where, delete, array

class Request:
	# key = date, value = loaction
	__house_dbLocations: dict[str: str] = dict({})
	__senate_dbLocations: dict[str: str] = dict({})

	def __set_dbLocation(self, soup: BeautifulSoup, isHouse: bool=True) -> None:
		'''
		Set data base locations

		# Params:
		soup - The BeutifulSoup object to search through\n
		isHouse - Store results in house DB or senate DB
		'''
		for itr in soup.find_all("key"):
			START: int = itr.string.rfind("for_") + 4
			END: int = itr.string.rfind(".json")

			if isHouse:
				self.__house_dbLocations[itr.string[START: END].replace("_", "-")] = itr.string
			else:
				self.__senate_dbLocations[itr.string[START: END].replace("_", "-")] = itr.string

	def __init__(self) -> None:
		# trades data bases
		houseDB: str = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/filemap.xml"
		senateDB: str = "https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/aggregate/filemap.xml"

		# all code in data bases
		# fix warnnings later
		houseSoup: BeautifulSoup = BeautifulSoup(get(houseDB).text)
		senateSoup: BeautifulSoup = BeautifulSoup(get(senateDB).text)

		self.__set_dbLocation(houseSoup)
		self.__set_dbLocation(senateSoup, False)

		# determin if date is within 30 days of current date
		from datetime import date
		TODAY_DATE: str = date.today().isoformat()

if __name__ == "__main__":
	req = Request()