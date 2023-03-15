from PyGUI import Button, Window, Text, Column, Input
from threading import Thread

from TradeData.Request import Request
from Helper.creds import winName
from Helper.helper import exitApp

class Pages:
	__housePages: dict[int, Column] = dict({})
	__houseSize = 0
	__senatePages: dict[int, Column] = dict({})
	__senateSize = 0

	# used to search by congress person
	__houseMap: dict[str, Column] = dict({})
	__senateMap: dict[str, Column] = dict({})

	# used to search by stock
	__stocksName: dict[str, Column] = dict({})
	__stocksTicker: dict[str, Column] = dict({})

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
			lst.append([Button("Back", key="rep_back")])

			if (lst[0][0].DisplayText in self.__houseMap) == False:
				self.__houseMap[lst[0][0].DisplayText] = Column(lst, size=(500, 500), scrollable=True)
			else:
				del self.__houseMap[lst[0][0].DisplayText].Rows[-1]
				for row in lst[1:]:
					self.__houseMap[lst[0][0].DisplayText].add_row(row[0])
		else:
			lst.append([Button("Back", key="sen_back")])

			if (lst[0][0].DisplayText in self.__senateMap) == False:
				self.__senateMap[lst[0][0].DisplayText] = Column(lst, size=(500, 500), scrollable=True)
			else:
				del self.__senateMap[lst[0][0].DisplayText].Rows[-1]
				for row in lst[1:]:
					self.__senateMap[lst[0][0].DisplayText].add_row(row[0])

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

		else:
			self.__senatePages[self.__senateSize] = col
			self.__senateSize += 1

			if self.__senateSize > 1:
				col.add_row(Text(f"Page: {self.__senateSize}"), Button("Prev Page", key="prev_sen"), Button("Next Page", key="nxt_sen"))
			else:		
				col.add_row(Text(f"Page: {self.__senateSize}"), Button("Next Page", key="nxt_sen"))

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

	def search(self, name: str, isHouse: bool) -> Column or None:
		'''
		Search for a congress person via their name

		# Params:
		name - The name of the congress person\n
		isHouse - True if the congress person is in the house else False

		# Returns:
		A Column object that contains all the trade data of that congress
		person. If that congress person cannot be found return None
		'''
		if isHouse:
			if (name in self.__houseMap):
				return self.__houseMap[name]
		else:
			if (name in self.__senateMap):
				return self.__senateMap[name]

	def emptyCheck(self) -> None:
		'''
		Add a line of text asking the user if they want to download more data
		from either house and or senate DB if there have been no trades in 30
		days
		'''
		if not self.__houseMap:
			self.__housePages[0].add_row(Text("There were no trades during the last 30 days. Do you want to download more data?"))
			self.__housePages[0].add_row(Button("Yes", key="rep_yes", pad=(121, None)))
		elif not self.__senateMap:
			self.__senatePages[0].add_row(Text("There were no trades during the last 30 days. Do you want to download more data?"))
			self.__senatePages[0].add_row(Button("Yes", key="sen_yes", pad=(242, None)))

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

pages = Pages()
MAX_TRADE_CNT = 5

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
							[assetType], [_type], [amt], [comment], [button], [line]], False)
					else:
						pages.updateMap([[name], [transDate], [owner], [assetDesc],
							[assetType], [_type], [amt], [comment], [line]], False)

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
		exitApp(event, data)

		if len(layout) > 3:
			del layout[3]

		try:
			days = int(values["days"].strip())

			if days > 1095:
				layout.append([Text("Cannot enter a value that is greater than 1095", text_color="red")])
				data.close()
				data = Window(winName, layout, modal=True)
				continue
			else:
				request = Request(days)
		except:
			layout.append([Text("Please only type numbers", text_color="red")])
			data.close()
			data = Window(winName, layout, modal=True)
		else:
			break

	request.download()

	createLeftSide = Thread(target=leftSide, args=(request.loadedHouse,))
	createRightSide = Thread(target=rightSide, args=(request.loadedSenate,))

	createLeftSide.start()
	createRightSide.start()

	createLeftSide.join()
	createRightSide.join()

	del createLeftSide
	del createRightSide
	del request

	data.close()
	repPage = 0
	senPage = 0
	HOUSE_SIZE = pages.houseSize
	SENATE_SIZE = pages.senateSize

	pages.emptyCheck()
	data = Window(winName, [[pages.getPage(repPage, True), pages.getPage(senPage, False)]])

	while True:
		event, values = data.read()
		exitApp(event, data)

		# click next page button
		if event == "nxt_rep":
			if repPage < HOUSE_SIZE:
				repPage += 1
				temp = displayPage(repPage, senPage, HOUSE_SIZE, True)

				if temp:
					data.close()
					data = temp
				else:
					repPage -= 1

				del temp

		elif event == "nxt_sen":
			if senPage < SENATE_SIZE:
				senPage += 1
				temp = displayPage(repPage, senPage, SENATE_SIZE, False)

				if temp:
					data.close()
					data = temp
				else:
					senPage -= 1

				del temp

		# click prev page button
		elif event == "prev_rep":
			if repPage < HOUSE_SIZE:
				repPage -= 1
				temp = displayPage(repPage, senPage, HOUSE_SIZE, True)

				if temp:
					data.close()
					data = temp
				else:
					repPage += 1

				del temp

		elif event == "prev_sen":
			if senPage < SENATE_SIZE:
				senPage -= 1
				temp = displayPage(repPage, senPage, SENATE_SIZE, False)

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

			if temp:
				temp = Window(winName, [[temp, data.Rows[0][1]]])
				data.close()
				data = temp
			del temp

		elif event == "sen_search":
			temp = pages.search("Name: " + values["sen_name"], False)

			if temp:
				temp = Window(winName, [[data.Rows[0][0], temp]])
				data.close()
				data = temp
			del temp

		# if user exits the search
		elif((event == "rep_back") or (event == "sen_back")):
			data.close()
			data = displayPage(repPage, senPage, HOUSE_SIZE, True)
