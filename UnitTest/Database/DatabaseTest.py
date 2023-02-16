from sys import argv, path

path[0] = path[0][:path[0].rfind("\\")]
path[0] = path[0][:path[0].rfind("\\")]

from Database import Database

class UnitTest(Database):
	def __init__(self) -> None:
		super.__init__()

if __name__ == "__main__":
	test = UnitTest()