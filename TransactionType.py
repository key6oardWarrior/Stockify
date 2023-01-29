from enum import Enum

class Types(Enum):
	Buy = 0,
	Sell = 1,
	Exchange = 2,
	Received = 3

def type_to_str(type_: Types) -> str:
	if type_ == Types.Buy:
		return "Buy"

	if type_ == Types.Sell:
		return "Sell"

	if type_ == Types.Exchange:
		return "Exchange"

	return "Received"