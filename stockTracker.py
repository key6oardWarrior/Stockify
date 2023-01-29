from Transaction_Innerface import ITransaction, Types

breq = ITransaction("https://www.capitoltrades.com/trades?txType=buy&txDate=30d&page=", Types.Buy)

for ii in range(breq.pages):
	breq.orgnizeData(breq.tagSearch(ii, "div", "q-table-wrapper").find_all("span"))

print(breq.name_and_trade)
