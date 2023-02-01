from bs4 import BeautifulSoup
from Table import Table

class Request:
	# Politician's names and what trades they have made
	__table: Table = Table()
	# each page's code as BeautifulSoup objects
	__soupArr: list[BeautifulSoup] = []
	# how many pages does the site have
	__NUM_PAGES: int

	def __moreSoup(self, browser, SITE: str) -> None:
		'''
		Add BeautifulSoup objects to the soup array

		# Params:
		browser - The browser being used to get the HTML data\n
		SITE - The website to visit
		'''
		from time import sleep

		WAIT = 0.2
		browser.get(SITE)
		sleep(WAIT) # wait for page to fully load
		self.__soupArr.append(BeautifulSoup(browser.page_source, "html.parser"))
		browser.close()

	def __setTable(self) -> None:
		for ii in range(0, len(self.__poly_trade), 2):
			self.__table.addRow(self.__poly_trade[ii].string,
				self.__poly_trade[ii+1].string)

	def __init__(self, SITE: str) -> None:
		'''
		Get Request object (aka requests.models.Response object). this contains
		all data about the site's data
		'''
		from Types import Browser, setBrowser, pickBrowser

		cnt = 1
		BROWSER_TYPE: Browser = setBrowser()

		self.__moreSoup(pickBrowser(BROWSER_TYPE), SITE + str(cnt))
		try:
			self.__NUM_PAGES = int(self.tagSearch(cnt-1, "div", "q-pagination")
				.find_all("b")[1])
		except:
			self.__NUM_PAGES = 1

		soupSearch = self.tagSearch(cnt-1, "tbody")
		# make global objects to pass large objects "by ref"
		self.__poly_trade = soupSearch.find_all("h3") # Politician and their trade
		self.__setTable()

		while cnt < self.__NUM_PAGES:
			cnt += 1

			self.__moreSoup(pickBrowser(BROWSER_TYPE), SITE + str(cnt))
			soupSearch = self.tagSearch(cnt-1, "tbody").find_all("h3")
			self.__poly_trade.extend(soupSearch.find_all("h3"))
			self.__setTable()

		# delete useless large objects
		del self.__poly_trade

	def tagSearch(self, INDEX: int, TAG: str, CLASS_: str=None, ID: str=None):
		'''
		Find all tags that are grouped under the given tag

		# Params:
		INDEX - Which page to search\n
		TAG - HTML tag to be searched for\n
		CLASS_ - Find every tag that has that 
		'''
		if CLASS_ and ID:
			raise AssertionError("Cannot search both class and id")

		if CLASS_:
			return self.__soupArr[INDEX].find(TAG, class_=CLASS_)
		return self.__soupArr[INDEX].find(TAG, id=ID)

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
	def pages(self) -> int:
		return self.__NUM_PAGES

	@property
	def table(self) -> Table:
		return self.__table

if __name__ == "__main__":
	breq = Request("https://www.capitoltrades.com/trades?txType=buy&txDate=30d&page=")