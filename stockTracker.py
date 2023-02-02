from Transaction_Innerface import ITransaction, Types

buyStocks = ITransaction("https://www.capitoltrades.com/trades?txType=buy&txDate=30d&page=", Types.Buy)
sellStocks = ITransaction("https://www.capitoltrades.com/trades?txType=sell&txDate=30d&page=", Types.Sell)

from os import remove
remove("geckodriver.log") # delete log files from automating browser