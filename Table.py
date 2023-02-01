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

	def __init__(self) -> None:
		from os.path import exists

		if exists("trades.txt"):
			self.__file = open("trades.txt", "a")
		else:
			self.__file = open("trades.txt", "w")

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

	def appendRow(self, NAME: str, ISSUER: list[str] or str) -> None:
		if type(ISSUER) == list:
			self.__politician[NAME].issuer.extend(ISSUER)
		else:
			self.__politician[NAME].issuer.append(ISSUER)

	def saveRows(self) -> None:
		self.__file.write(self.__politician)

	def getPolitician(self, NAME: str) -> Row:
		return self.__politician[NAME]

	@property
	def politician(self) -> None:
		return self.__politician

	def compareRows(self) -> None:
		'''
		Compare the saved rows to the rows downloaded from the internet
		'''
		pass

if __name__ == "__main__":
	table = Table()
	table.addRow("Jeff", "Google")
	table.addRow("Jeff", "Microsoft")

	table.addRow("Jake", "Facebook")
	table.addRow("Josh", "Amazon")

	print(table.getPolitician("Josh").issuer)