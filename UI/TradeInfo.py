from PyGUI import Button, Window, Text, Column, Input
from threading import Thread

from TradeData.Request import Request
from Helper.creds import winName
from Helper.helper import exitApp, exit

class Pages:
	__housePages: dict[int, Column] = dict({})
	__houseSize = 0
	__senatePages: dict[int, Column] = dict({})
	__senateSize = 0

	# used to search by congress person
	__houseMap: dict[str, Column] = dict({})
	__senateMap: dict[str, Column] = dict({})

	# used to search by stock
	__houseTickers: dict[str, Column] = dict({})
	__senateTickers: dict[str, Column] = dict({})

	__days = 0

	def __init__(self) -> None:
		pass

	def updateMap(self, lst: list[list], isHouse: bool) -> None:
		'''
		Update the houseMap and senateMap to make searching for a given
		congress person easier

		# Params:
		lst - A 2D list that contains all the elements that are needed to
		create all the UI elements for a given congress person\n
		isHouse - True if lst is from house member else False
		'''
		if isHouse:
			button = Button("Back", key="rep_back")

			name: str = lst[0][0].DisplayText.lower()
			if (name in self.__houseMap) == False:
				self.__houseMap[name] = Column(lst, size=(500, 500), scrollable=True)
				self.__houseMap[name].add_row(button)
			else:
				del self.__houseMap[name].Rows[-1]
				for row in lst[1:]:
					self.__houseMap[name].add_row(row[0])

				self.__houseMap[name].add_row(button)
 
			# add the stock's ticker name to the map
			tickerName: str = lst[2][0].DisplayText
			tickerName = tickerName[tickerName.find(" ")+1:]
			low = tickerName.lower()

			if (low in self.__houseTickers) == False:
				self.__houseTickers[low] = Column(lst, size=(500, 500), scrollable=True)
				self.__houseTickers[low].add_row(button)
			else:
				del self.__houseTickers[low].Rows[-1]
				for row in lst:
					self.__houseTickers[low].add_row(row[0])

				self.__houseTickers[low].add_row(button)

		else:
			lst.append([Button("Back", key="sen_back")])

			name: str = lst[0][0].DisplayText.lower()
			if (name in self.__senateMap) == False:
				self.__senateMap[name] = Column(lst, size=(500, 500), scrollable=True)
			else:
				del self.__senateMap[name].Rows[-1]
				for row in lst[1:]:
					self.__senateMap[name].add_row(row[0])

	def addPage(self, col: Column, isHouse: bool) -> None:
		'''
		Since PyGUI can only hold a maxium number of rows once it cannot hold
		anymore the overflow data is sent to another page. A page in this
		sense is another Column object that will be used to display more data

		# Params:
		col - Column object for containing all the page's data\n
		isHouse - True if house of rep else false
		'''
		if isHouse:
			self.__housePages[self.__houseSize] = col
			self.__houseSize += 1

			if self.__houseSize > 1:
				col.add_row(Text(f"Page: {self.__houseSize}"), Button("Prev Page", key="prev_rep"), Button("Next Page", key="nxt_rep"))
			else:
				col.add_row(Text(f"Page: {self.__houseSize}"), Button("Next Page", key="nxt_rep"))
			col.add_row(Text("Do you want to see more, or less days of trading data"), Button("Yes", key="rep_yes"))

		else:
			self.__senatePages[self.__senateSize] = col
			self.__senateSize += 1

			if self.__senateSize > 1:
				col.add_row(Text(f"Page: {self.__senateSize}"), Button("Prev Page", key="prev_sen"), Button("Next Page", key="nxt_sen"))
			else:		
				col.add_row(Text(f"Page: {self.__senateSize}"), Button("Next Page", key="nxt_sen"))
			col.add_row(Text("Do you want to see more, or less days of trading data"), Button("Yes", key="sen_yes"))

		col.add_row(Text("------------------"))

	def getPage(self, pageNum: int, isHouse: bool) -> Column:
		'''
		# Params:
		pageNum - Which page to return. This method does not check if pageNum
		is referencing a page that does not exists. UI should always pass
		valid page numbers to this method. This method is not error handled\n
		isHouse - True if returning house page else False

		# Returns:
		A Column object that will represent a page with all trade data relevant
		to that page
		'''
		if isHouse:
			return self.__housePages[pageNum]

		return self.__senatePages[pageNum]

	def search(self, name: str, isHouse: bool) -> Column or list[list]:
		'''
		Search for a congress person via their name

		# Params:
		name - The name of the congress person\n
		isHouse - True if the congress person is in the house else False

		# Returns:
		A Column object that contains all the trade data of that congress
		person. If that congress person cannot be found return None
		'''
		name = name.lower().strip()
		if isHouse:
			if (name in self.__houseMap):
				return self.__houseMap[name]
		else:
			if (name in self.__senateMap):
				return self.__senateMap[name]

		if self.__days > 1:
			return [Text(f"Either that congress person has not made a trade in {self.__days} days, or he/she does not exist", text_color="red")]
		else:
			return [Text(f"Either that congress person has not made a trade in {self.__days} day, or he/she does not exist", text_color="red")]

	def searchTickers(self, name: str, isHouse: bool) -> Column or None:
		'''
		Find all stocks that have the same name

		# Params:
		name - The tickers name\n
		isHouse - True if the congress person is in the house else False

		# Return:
		A Column object that contains all the trades of a given stock
		'''
		name = name.lower().strip()
		if isHouse:
			if (name in self.__houseTickers.keys()) == True:
				return self.__houseTickers[name]
		else:
			if (name in self.__senateTickers.keys()):
				return self.__senateTickers[name]

		if self.__days > 1:
			return [Text(f"Either that ticker has not been traded in {self.__days} days, or it does not exist", text_color="red")]
		else:
			return [Text(f"Either that ticker has not been traded in {self.__days} day, or it does not exist", text_color="red")]

	def clearRep(self) -> None:
		'''
		Clear all data about House members
		'''
		self.__houseMap.clear()
		self.__housePages.clear()
		self.__houseTickers.clear()
		self.__houseSize = 0

	def clearSen(self) -> None:
		'''
		Clear all data about Senate members
		'''
		self.__senateMap.clear()
		self.__senatePages.clear()
		self.__senateTickers.clear()
		self.__senateSize = 0

	def emptyCheck(self) -> None:
		'''
		Add a line of text asking the user if they want to download more data
		from either house and or senate DB if there have been no trades in the
		time selected
		'''
		if not self.__houseMap:
			self.__housePages[0].add_row(Text(f"There were no trades during the last {self.__days} days. Do you want to download more data?"))
			self.__housePages[0].add_row(Button("Yes", key="rep_yes", pad=(121, None)))

		if not self.__senateMap:
			self.__senatePages[0].add_row(Text(f"There were no trades during the last {self.__days} days. Do you want to download more data?"))
			self.__senatePages[0].add_row(Button("Yes", key="sen_yes", pad=(242, None)))

	def removeLastNextButton(self) -> None:
		'''
		Removes the "Next Page" button from the last page.
		'''
		del self.__housePages[self.__houseSize-1].Rows[-3][-1]
		del self.__senatePages[self.__senateSize-1].Rows[-3][-1]

	@property
	def houseSize(self) -> int:
		'''
		# Returns:
		How many pages the house of representives have
		'''
		return self.__houseSize

	@property
	def senateSize(self) -> int:
		'''
		# Returns:
		How many pages the senate has
		'''
		return self.__senateSize

	@property
	def days(self) -> int:
		return self.__days

	@days.setter
	def days(self, days: int) -> None:
		self.__days = days

pages = Pages()
MAX_TRADE_CNT = 5
MAX_DAYS = 1095

def createHeadLine(isHouse: bool) -> Column:
	'''
	Every page needs to have the same header

	# Params:
	isHouse - True if creating header for the house dataset else False

	# Returns:
	A Column object that will contain the header
	'''
	if isHouse:
		return Column(
			[
				[Text("House of Representives' Trades:", pad=(200, 0))],
				[Button("Search", key="rep_search"), Text("Enter House Rep's full name:"), Input(key="rep_name", size=(33, None))],
				[Button("Search", key="houseTicker"), Text("Enter the ticker name of the stock:"), Input(key="rep_ticker", size=(27, None))],
				[Text("-------------------------------------------------------------------------------------------------------------------------")]
			],
			size=(500, 500), scrollable=True
		)

	return Column(
		[
			[Text("Senate's Trades:", pad=(200, 0))],
			[Button("Search", key="sen_search"), Text("Enter Senator's full name:"), Input(key="sen_name", size=(33, None))],
			[Text("-------------------------------------------------------------------------------------------------------------------------")]
		],
		size=(500, 500), scrollable=True
	)

def displayPage(repPage: int, senPage: int, SIZE: int, isHouse: bool) -> Window | None:
	'''
	Create a Window object that will display both house and senate Column objs

	# Params:
	repPage - Which house page to display\n
	senPage - Which senate page to display\n
	SIZE - The max number of pages that house or senate pages can have\n
	isHouse - True if changing house page else False

	# Returns:
	A Window object to display all data. If the Window cannot be created return
	None
	'''
	if isHouse:
		if((repPage < SIZE) and (repPage >= 0)):
			return Window(winName, [[pages.getPage(repPage, True), pages.getPage(senPage, False)]])
	else:
		if((senPage < SIZE) and (senPage >= 0)):
			return Window(winName, [[pages.getPage(repPage, True), pages.getPage(senPage, False)]])

def rightSide(senateTrades) -> None:
	'''
	A child thread that creates and stores all pages that will be displayed on
	the right side of the screen.

	# Params:
	senateTrades - All the trades that were loaded from json files. See Request
	class
	'''
	rightCol: Column = createHeadLine(False)
	tradeCnt = 0

	for day in senateTrades:
		for trader in day:
			name = Text("Name: " + trader["first_name"] + " " + trader["last_name"], key="name")
			rightCol.add_row(name)
			trades = trader["transactions"]

			if trades:
				cnt = 1
				SIZE = len(trades)

				for trade in trades:
					transDate = Text("\tTransaction Date: " + trade["transaction_date"])
					rightCol.add_row(transDate)
					owner = Text("\tOwner: " + trade["owner"])
					rightCol.add_row(owner)
					assetDesc = Text("\tAsset Description: " + trade["asset_description"])
					rightCol.add_row(assetDesc)
					assetType = Text("\tAsset Type: " + trade["asset_type"])
					rightCol.add_row(assetType)
					_type = Text("\tType: " + trade["type"])
					rightCol.add_row(_type)
					amt = Text("\tAmount: " + trade["amount"])
					rightCol.add_row(amt)
					comment = Text("\tComment: " + trade["comment"])
					rightCol.add_row(comment)
					ticker = Text("\tTicker: " + trade["ticker"])
					rightCol.add_row(ticker)

					button = None
					if trade["asset_type"] == "Stock":
						button = Button("Trade This Stock")
						rightCol.add_row(button)

					if trade["asset_type"] == "Stock Option":
						button = Button("Trade This Option")
						rightCol.add_row(button)

					line = Text("\t------------------")
					if button:
						pages.updateMap([[name], [transDate], [owner], [assetDesc],
							[assetType], [_type], [amt], [comment], [ticker], [button], [line]], False)
					else:
						pages.updateMap([[name], [transDate], [owner], [assetDesc],
							[assetType], [_type], [amt], [comment], [ticker], [line]], False)

					if cnt != SIZE:
						rightCol.add_row(line)
						cnt += 1

			rightCol.add_row(Text("------------------"))
			tradeCnt += 1

			if tradeCnt >= MAX_TRADE_CNT:
				pages.addPage(rightCol, False)
				rightCol = createHeadLine(False)
				tradeCnt = 0

	if tradeCnt < MAX_TRADE_CNT:
		pages.addPage(rightCol, False)

def leftSide(houseTrades) -> None:
	'''
	A child thread that creates and stores all pages that will be displayed on
	the left side of the screen.

	# Params:
	houseTrades - All the trades that were loaded from json files. See Request
	class
	'''
	leftCol: Column = createHeadLine(True)
	tradeCnt = 0

	for day in houseTrades:
		for trader in day:
			name = Text("Name: " + trader["name"], key="name")
			leftCol.add_row(name)
			trades = trader["transactions"]

			if trades:
				cnt = 1
				SIZE = len(trades)

				for trade in trades:
					owner = Text("\tOwner: " + str(trade["owner"]))
					leftCol.add_row(owner)
					ticker = Text("\tTicker: " + trade["ticker"])
					leftCol.add_row(ticker)
					desc = Text("\tDescription: " + trade["description"])
					leftCol.add_row(desc)
					transDate = Text("\tTransaction Date: " + trade["transaction_date"])
					leftCol.add_row(transDate)
					transType = Text("\tTransaction Type: " + trade["transaction_type"])
					leftCol.add_row(transType)
					amt = Text("\tAmount: " + trade["amount"])
					leftCol.add_row(amt)
					cap = Text("\tCap Gains Over 200: " + str(trade["cap_gains_over_200"]))
					leftCol.add_row(cap)
					button = Button("Trade This Stock")
					leftCol.add_row(button)

					line = Text("\t------------------")
					pages.updateMap([[name], [owner], [ticker], [desc],
						[transDate], [transType], [amt], [cap], [button],
						[line]], True)

					if cnt != SIZE:
						leftCol.add_row(line)
						cnt += 1

			leftCol.add_row(Text("------------------"))
			tradeCnt += 1

			if tradeCnt >= MAX_TRADE_CNT:
				pages.addPage(leftCol, True)
				leftCol = createHeadLine(True)
				tradeCnt = 0

	if tradeCnt < MAX_TRADE_CNT:
		pages.addPage(leftCol, True)

def dataVisulization(request: Request) -> None:
	request.download()
	createLeftSide = Thread(target=leftSide, args=(request.loadedHouse,))
	createRightSide = Thread(target=rightSide, args=(request.loadedSenate,))

	createLeftSide.start()
	createRightSide.start()

	createLeftSide.join()
	createRightSide.join()

def dataScreen() -> None:
	'''
	Display all congress trade data
	'''
	request: Request
	layout = [
		[Text("How many past days of congress stock trading do you want to see (up to 1095 days ago):"), Input(key="days")],
		[Text("Depending on your internet speed this could take a few seconds, or a few mins. The app may go to sleep, so please wait")],
		[Button("Submit", key="sub")]
	]

	data = Window(winName, layout, modal=True)

	while True:
		event, values = data.read()
		if exitApp(event, data, True):
			exit(0)

		if len(layout) > 3:
			del layout[3]

		values["days"] = values["days"].strip()
		if values["days"].isdigit():
			days = int(values["days"])

			if((days > MAX_DAYS) or (days < 1)):
				layout.append([Text("Cannot enter a value that is greater than 1095, or less than 1", text_color="red")])
				data.close()
				data = Window(winName, layout, modal=True)
			else:
				pages.days = days
				request = Request(days)
				break
		else:
			layout.append([Text("Please only type numbers", text_color="red")])
			data.close()
			data = Window(winName, layout, modal=True)

	dataVisulization(request)

	data.close()
	repPage = 0
	senPage = 0
	_houseSize = pages.houseSize
	_senateSize = pages.senateSize
	pages.removeLastNextButton()

	pages.emptyCheck()
	data = Window(winName, [[pages.getPage(repPage, True), pages.getPage(senPage, False)]])
	# if an error has been added to either left or right side of Window
	isAdded: list[bool] = [False, False]

	while True:
		event, values = data.read()
		if exitApp(event, data, True):
			exit(0)

		if isAdded[0]:
			del data.Rows[0][0].Rows[0]
			isAdded[0] = False

		if isAdded[1]:
			del data.Rows[0][1].Rows[0]
			isAdded[1] = False

		# click next page button
		if event == "nxt_rep":
			if repPage < _houseSize:
				repPage += 1
				temp = displayPage(repPage, senPage, _houseSize, True)

				if temp:
					data.close()
					data = temp
				else:
					repPage -= 1

				del temp

		elif event == "nxt_sen":
			if senPage < _senateSize:
				senPage += 1
				temp = displayPage(repPage, senPage, _senateSize, False)

				if temp:
					data.close()
					data = temp
				else:
					senPage -= 1

				del temp

		# click prev page button
		elif event == "prev_rep":
			if repPage < _houseSize:
				repPage -= 1
				temp = displayPage(repPage, senPage, _houseSize, True)

				if temp:
					data.close()
					data = temp
				else:
					repPage += 1

				del temp

		elif event == "prev_sen":
			if senPage < _senateSize:
				senPage -= 1
				temp = displayPage(repPage, senPage, _senateSize, False)

				if temp:
					data.close()
					data = temp
				else:
					senPage += 1

				del temp

		# if user runs a search
		elif event == "rep_search":
			if ("Hon. " not in values["rep_name"]):
				temp = pages.search("Name: Hon. " + values["rep_name"], True)
			else:
				temp = pages.search("Name: " + values["rep_name"], True)

			if type(temp) == Column:
				temp = Window(winName, [[temp, data.Rows[0][1]]])
				data.close()
				data = temp
			else:
				data.Rows[0][0].Rows.insert(0, temp)
				tempWin = Window(winName, [[data.Rows[0][0], data.Rows[0][1]]])
				data.close()
				data = tempWin
				del tempWin
				isAdded[0] = True

			del temp

		elif event == "sen_search":
			temp = pages.search("Name: " + values["sen_name"], False)

			if type(temp) == Column:
				temp = Window(winName, [[data.Rows[0][0], temp]])
				data.close()
				data = temp
			else:
				data.Rows[0][1].Rows.insert(0, temp)
				tempWin = Window(winName, [[data.Rows[0][0], data.Rows[0][1]]])
				data.close()
				data = tempWin
				del tempWin
				isAdded[1] = True
			del temp

		# if user exits the search
		elif((event == "rep_back") or (event == "sen_back")):
			data.close()
			data = displayPage(repPage, senPage, _houseSize, True)

		# if user wants more data
		elif((event == "rep_yes") or (event == "sen_yes")):
			try: # just incase it has already been garbage collected
				del request
			except:
				pass
			
			o_layout = [[Text("Enter how many days of trading data you want:"), Input(key="retype")], [Button("Submit"), Button("Exit")]]
			O_SIZE = len(o_layout)
			delButton = False
			while True:
				overlayed = Window(winName, o_layout)
				o_event, o_values = overlayed.read()

				if exitApp(o_event, overlayed):
					break

				if len(o_layout) > O_SIZE:
					del o_layout[-1]

				if len(o_layout) > 3:
					del o_layout[3]

				o_values["retype"] = o_values["retype"].strip()
				if o_values["retype"].isdigit():
					days = int(o_values["retype"])

					if((days > MAX_DAYS) or (days < 1)):
						o_layout.append([Text("Cannot enter a value that is greater than 1095, or less than 1", text_color="red")])
						overlayed.close()
						overlayed = Window(winName, o_layout, modal=True)
						continue
					else:
						pages.days = days
						request = Request(days)
				else:
					o_layout.append([Text("Please only type numbers", text_color="red")])
					overlayed.close()
					overlayed = Window(winName, o_layout, modal=True)
					continue
				
				pages.clearRep()
				pages.clearSen()
				dataVisulization(request)
				pages.emptyCheck()
				data.close()
				_houseSize = pages.houseSize
				_senateSize = pages.senateSize
				repPage = 0
				senPage = 0
				data = Window(winName, [[pages.getPage(repPage, True), pages.getPage(senPage, False)]])

				overlayed.close()
				delButton = True
				break

			if delButton:
				pages.removeLastNextButton()

		# if user wants to do a ticker search
		elif event == "houseTicker":
			temp = pages.searchTickers(values["rep_ticker"], True)

			if type(temp) == Column:
				tempWin = Window(winName, [[temp, data.Rows[0][1]]])
				data.close()
				data = tempWin
			else:
				data.Rows[0][0].Rows.insert(0, temp)
				tempWin = Window(winName, [[data.Rows[0][0], data.Rows[0][1]]])
				data.close()
				data = tempWin
				del tempWin
				isAdded[0] = True

		elif event == "senateTicker":
			temp = pages.searchTickers(values["sen_ticker"], False)
			tempWin = Window(winName, [[data.Rows[0][0], temp]])
			data.close()
			data = tempWin
