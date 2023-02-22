from os import mkdir
from sys import platform
from shutil import move

if platform == "win32":
	dataDir = "C:\\Users\\Lewjb\\AppData\\Local\\Stockify"
	mkdir(dataDir)
elif((platform == "linux") or (platform == "linux2")):
	dataDir = "/usr/local/Stockify"
	mkdir(dataDir)
else: # darwin
	dataDir = "/usr/local/bin/Stockify"
	mkdir(dataDir)

move("bins", dataDir)