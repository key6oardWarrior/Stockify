from bs4 import BeautifulSoup
from requests import get
from wget import download
from numpy import where, delete, array

class Request:
	# key = date, value = loaction
	__house_dbLocations: dict[str: str] = dict({})
	__senate_dbLocations: dict[str: str] = dict({})
	__housePastDates: list = []
	__senatePastDates: list = []
	__senate_db = "https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/"
	__house_db = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/"

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
				self.__house_dbLocations[itr.string[START: END].replace("_", "/")] = itr.string
			else:
				self.__senate_dbLocations[itr.string[START: END].replace("_", "/")] = itr.string

	def __findDates(self, dates: list, isHouse: bool=True) -> None:
		'''
		Get all dates that are <= __pastDates ago

		# Params:
		dates - List of dates\n
		isHouse - Are dates for house or senate
		'''
		from datetime import date
		from dateutil import relativedelta
		from datetime import datetime

		TODAY_DATE: str = date.today().isoformat().replace("-", "/")
		TODAY_DATE: datetime = datetime.strptime(TODAY_DATE, "%Y/%m/%d")

		for _date in dates:
			PAST_DATE: datetime = datetime.strptime(_date, "%m/%d/%Y")
			diff = relativedelta.relativedelta(TODAY_DATE, PAST_DATE)

			if((diff.months < 1) and (diff.years == 0)):
				if isHouse:
					self.__housePastDates.append(_date)
				else:
					self.__senatePastDates.append(_date)

	def __init__(self) -> None:
		# trades data bases
		houseDB: str = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/filemap.xml"
		senateDB: str = "https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/aggregate/filemap.xml"

		# all code in data bases
		houseSoup: BeautifulSoup = BeautifulSoup(get(houseDB).text, features="lxml")
		senateSoup: BeautifulSoup = BeautifulSoup(get(senateDB).text, features="lxml")

		self.__set_dbLocation(houseSoup)
		self.__set_dbLocation(senateSoup, False)

		self.__findDates(self.__house_dbLocations.keys())
		self.__findDates(self.__senate_dbLocations.keys(), False)

if __name__ == "__main__":
	req = Request()