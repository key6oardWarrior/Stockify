from Transaction_Innerface import ITransaction, Types

breq = ITransaction("https://www.capitoltrades.com/trades?txType=buy&txDate=30d&page=", Types.Buy)

from os import remove
remove("geckodriver.log") # delete log files from automating browser