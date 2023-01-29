from bs4 import BeautifulSoup
from selenium import webdriver

class BuyReq:
	# Politician's names and what trades they have made
	__name_and_trade: dict[str, list] = dict({})
	# each page's code as BeautifulSoup objects
	__soupArr: list[BeautifulSoup] = []
	# how many pages does the site have
	__NUM_PAGES: int

	def __init__(self, SITE: str) -> None:
		'''
		Get Request object (aka requests.models.Response object). this contains
		all data about the site's data
		'''
		from time import sleep
		cnt = 1

		fireFox = webdriver.Firefox()
		fireFox.get(SITE + str(cnt))
		sleep(0.1) # wait for page to fully load
		self.__soupArr.append(BeautifulSoup(fireFox.page_source, "html.parser"))
		fireFox.close()

		BOLD_TAG = self.tagSearch(cnt-1, "div", "q-pagination").find_all("b")[1]
		self.__NUM_PAGES = int(BOLD_TAG.string)

		while cnt < self.__NUM_PAGES:
			cnt += 1
			fireFox = webdriver.Firefox()
			fireFox.get(SITE + str(cnt))
			sleep(0.1) # wait for page to fully load

			self.__soupArr.append(BeautifulSoup(fireFox.page_source,
				"html.parser"))
			fireFox.close()

	def tagSearch(self, INDEX: int, TAG: str, CLASS_: str=None, ID: str=None):
		'''
		Find all tags that are grouped under the given tag

		# Params:
		INDEX - Which page to search
		TAG - HTML tag to be searched for 
		CLASS_ - Find every tag that has that 
		'''
		if CLASS_ and ID:
			raise AssertionError("Cannot search both class and id")

		if CLASS_:
			return self.__soupArr[INDEX].find(TAG, class_=CLASS_)
		return self.__soupArr[INDEX].find(TAG, id=ID)

	def orgnizeData(self, rawHtmlData: list) -> None:
		'''
		Orgnizes raw HTML data so politician trades can be stored in a dict

		# Params:
		rawHtmlData - A list of HTML h3 tags that contain data on politician's
		trading. Each element is raw HTML data
		'''
		ii = 0
		print("Key:\n{Politician: [Traded Issuer, times traded]}")
		while ii < len(rawHtmlData)-1:
			NAME: str = rawHtmlData[ii].string
			TRADE: str = rawHtmlData[ii+1].string

			if NAME in self.__name_and_trade:
				if TRADE in self.__name_and_trade[NAME]:
					self.__name_and_trade[NAME][1] += 1
				else:
					self.__name_and_trade[NAME] = [TRADE, 1]
			else:
				self.__name_and_trade[NAME] = [TRADE, 1]

			ii += 2

	def soupArr(self, INDEX: int) -> BeautifulSoup:
		'''
		# Params:
		INDEX - Which page from the site to return

		# Returns:
		A BeautifulSoup object that contains all code for site.
		'''
		return self.__soupArr[INDEX]

	@property
	def soupArr(self) -> list[BeautifulSoup]:
		'''
		Get the HTML text of the entire soup
		'''
		return self.__soupArr

	@property
	def name_and_trade(self) -> dict[str, list]:
		return self.__name_and_trade

	@property
	def pages(self) -> int:
		return self.__NUM_PAGES

def println(lst):
	for i in lst:
		print(i, "\n")

if __name__ == "__main__":
	breq = BuyReq("https://www.capitoltrades.com/trades?txType=buy&txDate=30d&page=")

	for ii in range(breq.pages):
		breq.orgnizeData(breq.tagSearch(ii, "div").find_all("h3"))

	print(breq.name_and_trade)