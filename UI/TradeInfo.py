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
	col = Column([[Text("House Trades:")]], scrollable=True)

	for itr in houseTrades:
		for trader in itr:
			col.add_row(Text("Name: " + trader["name"]))
			trades = trader["transactions"]

			if trades:
				cnt = 1
				SIZE = len(trades)

				for trade in trades:
					col.add_row(Text("\tOwner: " + str(trade["owner"])))
					col.add_row(Text("\tTicker: " + trade["ticker"]))
					col.add_row(Text("\tDescription: " + trade["description"]))
					col.add_row(Text("\tTransaction Type: " + trade["transaction_type"]))
					col.add_row(Text("\tAmount: " + trade["amount"]))
					col.add_row(Text("\tCap Gains Over 200: " + str(trade["cap_gains_over_200"])))
					col.add_row(Button("Trade This Stock"))

					if cnt != SIZE:
						col.add_row(Text("\t------------------"))
						cnt += 1			

			col.add_row(Text("------------------"))

	col.add_row(Text("\nSenate Trades:"))
	for itr in senateTrades:
		for trader in itr:
			col.add_row(Text(trader["first_name"] + " " + trader["last_name"]))
			trades = trader["transactions"]

			if trades:
				cnt = 1
				SIZE = len(trades)

				for trade in trades:
					col.add_row(Text("Transaction Date: " +
						trade["transaction_date"]))
					col.add_row(Text("Owner: " + trade["owner"]))
					col.add_row(Text("Asset Description: " + trade["asset_description"]))
					col.add_row(Text("Asset Type: " + trade["asset_type"]))
					col.add_row(Text("Type: " + trade["type"]))
					col.add_row(Text("Amount: " + trade["amount"]))
					col.add_row(Text("Comment: " + trade["comment"]))

					if cnt != SIZE:
						col.add_row(Text("\t------------------"))
						cnt += 1

					if trade["asset_type"] == "Stock":
						col.add_row(Button("Trade This Stock"))

				col.add_row(Text("------------------"))

	col.add_row(Button("Exit"))
	data.close()
	data = Window(winName, [[col]], resizable=True, finalize=True)

	while True:
		event, values = data.read()
		exitApp(event, data)
