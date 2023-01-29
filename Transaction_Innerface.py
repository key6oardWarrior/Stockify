from Request import Request
from Types import Types

class ITransaction(Request):
	__TYPE: Types

	def __init__(self, SITE: str, TYPE: Types) -> None:
		super().__init__(SITE)
		self.__TYPE = TYPE

	@property
	def transcationType(self) -> Types:
		return self.__TYPE
