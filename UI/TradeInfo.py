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
	data.close()

	houseTrades = request.loadedHouse
	senateTrades = request.loadedSenate

	layout = []
	col = Column([[]], size=(500, 500), scrollable=True)

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

					if cnt != SIZE:
						col.add_row(Text("\t------------------"))
						cnt += 1			

			col.add_row(Text("------------------"))

	col.add_row(Button("Exit"))
	data = Window(winName, [[col]], resizable=True, finalize=True)

	while True:
		event, values = data.read()
		exitApp(event, data)
