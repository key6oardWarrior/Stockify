from PySimpleGUI.PySimpleGUI import Button, Window, Text, Column
from threading import Thread

from TradeData.Request import Request
from Helper.creds import winName
from Helper.helper import exitApp

def delete(request: Request) -> None:
	request.deleteAll()

def dataScreen() -> None:
	request = Request()
	layout = [
		[Button("View last 30 days of trading", key="30d"),
		Button("View last 3 years of trading", key="3y")],
		[Text("Depending on your internet speed this could take a few seconds, or a few mins. The app may go to sleep, so please wait")]
	]

	data = Window(winName, layout, modal=True)

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

	houseTrades = request.loadedHouse
	senateTrades = request.loadedSenate
	leftCol = Column([[Text("House Trades:")]], size=(500, 500), scrollable=True)

	for itr in houseTrades:
		for trader in itr:
			leftCol.add_row(Text("Name: " + trader["name"]))
			trades = trader["transactions"]

			if trades:
				cnt = 1
				SIZE = len(trades)

				for trade in trades:
					leftCol.add_row(Text("\tOwner: " + str(trade["owner"])))
					leftCol.add_row(Text("\tTicker: " + trade["ticker"]))
					leftCol.add_row(Text("\tDescription: " + trade["description"]))
					leftCol.add_row(Text("\tTransaction Type: " + trade["transaction_type"]))
					leftCol.add_row(Text("\tAmount: " + trade["amount"]))
					leftCol.add_row(Text("\tCap Gains Over 200: " + str(trade["cap_gains_over_200"])))
					leftCol.add_row(Button("Trade This Stock"))

					if cnt != SIZE:
						leftCol.add_row(Text("\t------------------"))
						cnt += 1

			leftCol.add_row(Text("------------------"))

	rightCol = Column([[Text("\nSenate Trades:")]], size=(500, 500), scrollable=True)
	for itr in senateTrades:
		for trader in itr:
			rightCol.add_row(Text("Name: " + trader["first_name"] + " " + trader["last_name"]))
			trades = trader["transactions"]

			if trades:
				cnt = 1
				SIZE = len(trades)

				for trade in trades:
					rightCol.add_row(Text("\tTransaction Date: " +
						trade["transaction_date"]))
					rightCol.add_row(Text("\tOwner: " + trade["owner"]))
					rightCol.add_row(Text("\tAsset Description: " + trade["asset_description"]))
					rightCol.add_row(Text("\tAsset Type: " + trade["asset_type"]))
					rightCol.add_row(Text("\tType: " + trade["type"]))
					rightCol.add_row(Text("\tAmount: " + trade["amount"]))
					rightCol.add_row(Text("\tComment: " + trade["comment"]))

					if trade["asset_type"] == "Stock":
						rightCol.add_row(Button("Trade This Stock"))

					if cnt != SIZE:
						rightCol.add_row(Text("\t------------------"))
						cnt += 1

				rightCol.add_row(Text("------------------"))

	data.close()
	data = Window(winName, [[leftCol, rightCol]], resizable=True, finalize=True)

	while True:
		event, values = data.read()
		exitApp(event, data)
