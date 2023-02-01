from json import dump, load

class Row:
	# Politician's name
	name: str
	# key = issuer name, value = stock's info
	issuer: list[str]
	__isInit = False

	def __init__(self) -> None:
		pass

	@property
	def isInit(self) -> bool:
		return self.__isInit

	@isInit.setter
	def isInit(self, val: bool) -> None:
		self.__isInit = val

class Table:
	# key = Politician's name, val = Row object
	__politician: dict[str: Row] = dict({})
	__newTrades: dict[str: list[str]] = dict({})

	def __init__(self) -> None:
		pass

	def addRow(self, NAME: str, ISSURER: list[str] or str) -> None:
		row: Row

		if (NAME in self.__politician):
			row = self.__politician[NAME]
		else:
			row = Row()
			row.name = NAME
			self.__politician[NAME] = row

		if row.isInit:
			if type(ISSURER) == list:
				row.issuer.extend(ISSURER)
			else:
				row.issuer.append(ISSURER)
		else:
			row.isInit = True
			if type(ISSURER) == list:
				row.issuer = ISSURER
			else:
				row.issuer = [ISSURER]

	def removeRow(self, NAME: str) -> None:
		del self.__politician[NAME]  

	def saveRows(self) -> None:
		with open("trades.json", "w") as file:
			dump(self.__newTrades, file)

	def compareRows(self) -> None:
		'''
		Compare the saved rows to the rows downloaded from the internet
		'''
		from os.path import exists
		saved: bool
		savedRows: dict[str: list[str]]

		if exists("trades.json"):
			with open('trades.json') as file:
				savedRows = load(file)
			saved = False
		else:
			saved = True

		if saved:
			for itr in self.__politician:
				self.__newTrades[itr] = self.__politician[itr].issuer

			self.saveRows()
			return

		for itr in self.__politician:
			if itr in savedRows.keys():
				if self.__politician[itr].issuer != savedRows[itr]:
					saved = True
					self.__newTrades[itr] = self.__politician[itr].issuer
			else:
				saved = True
				self.__newTrades[itr] = self.__politician[itr].issuer

		if saved:
			self.saveRows()

	def getPolitician(self, NAME: str) -> Row:
		return self.__politician[NAME]

	@property
	def politician(self) -> dict[str: Row]:
		return self.__politician

	@property
	def newTrades(self) -> dict[str: list[str]]:
		return self.__newTrades

if __name__ == "__main__":
	table = Table()
	table.addRow("Jeff", "Google")
	table.addRow("Jeff", "Microsoft")
	table.addRow("Jake", "Facebook")
	table.addRow("Josh", "Amazon")

	table.compareRows()
	table.saveRows()
	print(table.newTrades)