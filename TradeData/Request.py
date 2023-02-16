from json import load
from os.path import exists, join

from bs4 import BeautifulSoup
from requests import get
from wget import download

from helper import ConnectionError

class Request:
	# key = date, value = loaction of datebase
	__house_dbLocations: dict[str: str] = dict({})
	__senate_dbLocations: dict[str: str] = dict({})
	__housePastDates: list = []
	__senatePastDates: list = []
	__loadedSenate = []
	__loadedHouse = []
	__senate_db = "https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/"
	__house_db = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/"
	__HOUSE_PATH = "house"
	__SENATE_PATH = "senate"

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
		from datetime import date, datetime
		from dateutil import relativedelta

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

			if(((diff.months < 1) or (diff.days < 1)) and (diff.years < 1)):
				if isHouse:
					self.__housePastDates.append(STR_DATE)
				else:
					self.__senatePastDates.append(STR_DATE)
			else:
				break

	def __init__(self) -> None:
		from os import mkdir
		from os.path import isdir

		if isdir(self.__HOUSE_PATH) == False:
			mkdir(self.__HOUSE_PATH)
	
		if isdir(self.__SENATE_PATH) == False:
			mkdir(self.__SENATE_PATH)

		# trades data bases
		houseDB: str = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/filemap.xml"
		senateDB: str = "https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/aggregate/filemap.xml"

		# all code in data bases
		try:
			houseSoup: BeautifulSoup = BeautifulSoup(get(houseDB).text, features="lxml")
		except:
			raise ConnectionError(f"Could not get {houseDB}")

		try:
			senateSoup: BeautifulSoup = BeautifulSoup(get(senateDB).text, features="lxml")
		except:
			raise ConnectionError(f"Could not get {senateDB}")

		self.__set_dbLocation(houseSoup)
		self.__set_dbLocation(senateSoup, False)

		self.__findDates(iter(self.__house_dbLocations.keys()))
		self.__findDates(iter(self.__senate_dbLocations.keys()), False)

	def download(self) -> None:
		'''
		Download useful data found in house and senate DB
		'''
		for itr in self.__housePastDates:
			try:
				download(self.__house_db + self.__house_dbLocations[itr],
					join(self.__HOUSE_PATH, "house" + itr + ".json"))
			except:
				print("\ncould not download:", itr)

		for itr in self.__senatePastDates:
			try:
				download(self.__senate_db + self.__senate_dbLocations[itr],
					join(self.__SENATE_PATH, "senate" + itr + ".json"))
			except:
				print("\ncould not download :", itr)

	def downloadAll(self) -> None:
		'''
		Download all data found in house and senate DB
		'''
		for itr in self.__house_dbLocations:
			try:
				download(self.__house_db + self.__house_dbLocations[itr],
					join(self.__HOUSE_PATH, "house" + itr + ".json"))
			except:
				print("\ncould not download:", itr)

		for itr in self.__senate_dbLocations:
			try:
				download(self.__house_db + self.__senate_dbLocations[itr],
					join(self.__SENATE_PATH, "senate" + itr + ".json"))
			except:
				print("\ncould not download:", itr)

	def deleteAll(self) -> None:
		'''
		Delete all downloaded JSON files
		'''
		from os import removedirs
		removedirs(self.__HOUSE_PATH)
		removedirs(self.__SENATE_PATH)

	def __load(self, itr, SIZE: int, IS_HOUSE: bool=True) -> None:
		'''
		Load all downloaded data into primary memory

		# Params:
		itr - The dict iter
		SIZE - Size of object that itr came from
		'''
		ii = 0
		while ii < SIZE:
			date: str = next(itr)

			if IS_HOUSE:
				PATH: str = join(self.__HOUSE_PATH, f"house{date}.json")

				if exists(PATH):
					with open(PATH, "r") as file:
						self.__loadedHouse.append(load(file))
				else: # end loop if path not found
					return
			else:
				PATH: str = join(self.__SENATE_PATH, f"senate{date}.json")

				if exists(PATH):
					with open(PATH, "r") as file:
						self.__loadedSenate.append(load(file))
				else: # end loop if path not found
					return

			ii += 1

	def load(self) -> None:
		'''
		Load each JSON into primary memory
		'''
		self.__load(iter(self.__house_dbLocations.keys()),
			len(self.__house_dbLocations))
		self.__load(iter(self.__senate_dbLocations.keys()),
			len(self.__senate_dbLocations), False)

	@property
	def loadedSenate(self) -> list:
		return self.__loadedSenate

	@property
	def loadedHouse(self) -> list:
		return self.__loadedHouse