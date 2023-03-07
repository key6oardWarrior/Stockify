from PyGUI import Button, Window, Text, Column, Input
from threading import Thread

from TradeData.Request import Request
from Helper.creds import winName
from Helper.helper import exitApp

def delete(request: Request) -> None:
	request.deleteAll()

class Pages:
	__housePages = dict({})
	__houseSize = 0
	__senatePages = dict({})
	__senateSize = 0

	def __init__(self) -> None:
		pass

	def addPage(self, col: list, isHouse: bool) -> None:
		if isHouse:
			self.__housePages[self.__houseSize] = col
			self.__houseSize += 1

			if self.__houseSize > 1:
				col.append([Text(f"Page: {self.__houseSize}"), Button("Prev Page", key="prev_rep"), Button("Next Page", key="nxt_rep")])
			else:
				col.append([Text(f"Page: {self.__houseSize}"), Button("Next Page", key="nxt_rep")])

		else:
			self.__senatePages[self.__senateSize] = col
			self.__senateSize += 1

			if self.__senateSize > 1:
				col.append([Text(f"Page: {self.__senateSize}"), Button("Prev Page", key="prev_sen"), Button("Next Page", key="nxt_sen")])
			else:		
				col.append([Text(f"Page: {self.__senateSize}"), Button("Next Page", key="nxt_sen")])

	def getPage(self, pageNum: int, isHouse: bool) -> list:
		if isHouse:
			return self.__housePages[pageNum]

		return self.__senatePages[pageNum]

	@property
	def houseSize(self) -> int:
		return self.__houseSize

	@property
	def senateSize(self) -> int:
		return self.__senateSize

pages = Pages()
MAX_TRADE_CNT = 5

def createHeadLine(isHouse: bool) -> list:
	if isHouse:
		return [
				[Button("Search"), Text("Enter House Rep's full name:"), Input(key="rep_name")],
				[Text("House of Representives Trades:", pad=(200, 0))]
			]

	return [
			[Button("Search"), Text("Enter Senator's full name:"), Input(key="sen_name")],
			[Text("Senate's Trades:", pad=(200, 0))]
		]

def displayPage(repPage: int, senPage: int, SIZE: int, isHouse: bool) -> Window | None:
	if isHouse:
		if((repPage < SIZE) and (repPage >= 0)):
			return Window(winName, [[Column(pages.getPage(repPage, True), size=(500, 500), scrollable=True), Column(pages.getPage(senPage, False), size=(500, 500), scrollable=True)]])
	else:
		if((senPage < SIZE) and (senPage >= 0)):
			return Window(winName, [[Column(pages.getPage(repPage, True), size=(500, 500), scrollable=True), Column(pages.getPage(senPage, False), size=(500, 500), scrollable=True)]])

def rightSide(senateTrades) -> None:
	rightCol: list = createHeadLine(False)
	tradeCnt = 0

	for day in senateTrades:
		for trader in day:
			rightCol.append([Text("Name: " + trader["first_name"] + " " + trader["last_name"])])
			trades = trader["transactions"]

			if trades:
				cnt = 1
				SIZE = len(trades)

				for trade in trades:
					rightCol.append([Text("\tTransaction Date: " +
						trade["transaction_date"])])
					rightCol.append([Text("\tOwner: " + trade["owner"])])
					rightCol.append([Text("\tAsset Description: " + trade["asset_description"])])
					rightCol.append([Text("\tAsset Type: " + trade["asset_type"])])
					rightCol.append([Text("\tType: " + trade["type"])])
					rightCol.append([Text("\tAmount: " + trade["amount"])])
					rightCol.append([Text("\tComment: " + trade["comment"])])

					if trade["asset_type"] == "Stock":
						rightCol.append([Button("Trade This Stock")])

					if cnt != SIZE:
						rightCol.append([Text("\t------------------")])
						cnt += 1

				rightCol.append([Text("------------------")])
				tradeCnt += 1

				if tradeCnt >= MAX_TRADE_CNT:
					pages.addPage(rightCol, False)
					rightCol = createHeadLine(False)
					tradeCnt = 0

	if tradeCnt < MAX_TRADE_CNT:
		pages.addPage(rightCol, False)

def leftSide(houseTrades) -> None:
	leftCol: list = createHeadLine(True)
	tradeCnt = 0

	for day in houseTrades:
		for trader in day:
			leftCol.append([Text("Name: " + trader["name"])])
			trades = trader["transactions"]

			if trades:
				cnt = 1
				SIZE = len(trades)

				for trade in trades:
					leftCol.append([Text("\tOwner: " + str(trade["owner"]))])
					leftCol.append([Text("\tTicker: " + trade["ticker"])])
					leftCol.append([Text("\tDescription: " + trade["description"])])
					leftCol.append([Text("\tTransaction Date: " + trade["transaction_date"])])
					leftCol.append([Text("\tTransaction Type: " + trade["transaction_type"])])
					leftCol.append([Text("\tAmount: " + trade["amount"])])
					leftCol.append([Text("\tCap Gains Over 200: " + str(trade["cap_gains_over_200"]))])
					leftCol.append([Button("Trade This Stock")])

					if cnt != SIZE:
						leftCol.append([Text("\t------------------")])
						cnt += 1

			leftCol.append([Text("------------------")])
			tradeCnt += 1

			if tradeCnt >= MAX_TRADE_CNT:
				pages.addPage(leftCol, True)
				leftCol = createHeadLine(True)
				tradeCnt = 0

	if tradeCnt < MAX_TRADE_CNT:
		pages.addPage(leftCol, True)

def dataScreen() -> None:
	request = Request()
	layout = [
		[Button("View last 30 days of trading", key="30d"),
		Button("View last 3 years of trading", key="3y")],
		[Text("Depending on your internet speed this could take a few seconds, or a few mins. The app may go to sleep, so please wait")]
	]

	data = Window(winName, layout, modal=True)
	data.key_dict

	while True:
		event, values = data.read()
		exitApp(event, data)
		if event == "30d":
			request.download()
		else:
			request.downloadAll()

		break

	request.load()
	Thread(target=delete, args=(request,)).start()

	createLeftSide = Thread(target=leftSide, args=(request.loadedHouse,))
	createRightSide = Thread(target=rightSide, args=(request.loadedSenate,))

	createLeftSide.start()
	createRightSide.start()

	createLeftSide.join()
	createRightSide.join()

	data.close()
	repPage = 0
	senPage = 0
	HOUSE_SIZE = pages.houseSize
	SENATE_SIZE = pages.senateSize
	data = Window(winName, [[Column(pages.getPage(repPage, True), scrollable=True, size=(500, 500)), Column(pages.getPage(senPage, False), scrollable=True, size=(500, 500))]])

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
	
		elif event == "nxt_sen":
			if senPage < SENATE_SIZE:
				senPage += 1
				temp = displayPage(repPage, senPage, SENATE_SIZE, False)

				if temp:
					data.close()
					data = temp
				else:
					senPage -= 1

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

		elif event == "prev_sen":
			if senPage < SENATE_SIZE:
				senPage -= 1
				temp = displayPage(repPage, senPage, SENATE_SIZE, False)

				if temp:
					data.close()
					data = temp
				else:
					senPage += 1
				