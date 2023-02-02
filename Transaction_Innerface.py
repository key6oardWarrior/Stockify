from Request import Request
from Types import Types

class ITransaction(Request):
	__TYPE: Types

	def __init__(self, SITE: str, TYPE: Types) -> None:
		self.__TYPE = TYPE
		super().__init__(SITE)

	@property
	def transcationType(self) -> Types:
		return self.__TYPE
