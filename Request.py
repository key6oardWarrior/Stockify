from bs4 import BeautifulSoup
from requests import get
from wget import download
from json import load

class Request:
	# key = date, value = loaction of datebase
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
				self.__house_dbLocations[itr.string[START: END]] = itr.string
			else:
				self.__senate_dbLocations[itr.string[START: END]] = itr.string

	def __findDates(self, _date, isHouse: bool=True) -> None:
		'''
		Get all dates that are <= __pastDates ago

		# Params:
		dates - An iterator of dict.keys\n
		isHouse - Are dates for house or senate
		'''
		from datetime import date
		from dateutil import relativedelta
		from datetime import datetime

		TODAY_DATE: str = date.today().isoformat()
		TODAY_DATE: datetime = datetime.strptime(TODAY_DATE, "%Y-%m-%d")

		if isHouse:
			SIZE = len(self.__house_dbLocations)
		else:
			SIZE = len(self.__senate_dbLocations)

		# if there is less than 30 day difference append to list
		index = 0
		while index < SIZE:
			STR_DATE: str = next(_date)
			pastDate: datetime = datetime.strptime(STR_DATE, "%m_%d_%Y")
			diff = relativedelta.relativedelta(TODAY_DATE, pastDate)

			if((diff.months <= 1) and (diff.years <= 0)):
				if isHouse:
					self.__housePastDates.append(STR_DATE)
				else:
					self.__senatePastDates.append(STR_DATE)
			else:
				index = SIZE

	def __init__(self) -> None:
		# trades data bases
		houseDB: str = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/filemap.xml"
		senateDB: str = "https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/aggregate/filemap.xml"

		# all code in data bases
		houseSoup: BeautifulSoup = BeautifulSoup(get(houseDB).text, features="lxml")
		senateSoup: BeautifulSoup = BeautifulSoup(get(senateDB).text, features="lxml")

		self.__set_dbLocation(houseSoup)
		self.__set_dbLocation(senateSoup, False)

		self.__findDates(iter(self.__house_dbLocations.keys()))
		self.__findDates(iter(self.__senate_dbLocations.keys()), False)

	def download(self) -> None:
		'''
		Download useful data found in house and senate DB
		'''
		for itr in self.__housePastDates:
			download(self.__house_db + self.__house_dbLocations[itr],
				"house" + itr + ".json")

		for itr in self.__senatePastDates:
			download(self.__senate_db + self.__senate_dbLocations[itr],
				"senate" + itr + ".json")

	def downloadAll(self) -> None:
		'''
		Download all data found in house and senate DB
		'''
		for itr in self.__house_dbLocations:
			download(self.__house_db + self.__house_dbLocations[itr],
				"house" + itr + ".json")

		for itr in self.__senate_dbLocations:
			download(self.__house_db + self.__senate_dbLocations[itr],
				"senate" + itr + ".json")

	def deleteAll(self) -> None:
		'''
		Delete all downloaded JSON files
		'''
		from os.path import exists
		from os import remove

		for itr in self.__house_dbLocations:
			PATH = "house" + itr + ".json"

			if exists(PATH):
				remove(PATH)
			else:
				break

if __name__ == "__main__":
	req = Request()
	req.deleteAll()

	from os import remove
	# remove not needed files
	remove("geckodriver.log")