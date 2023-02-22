from os import mkdir
from shutil import move
from sys import platform

if platform == "win32":
	from os.path import expanduser

	dataDir = expanduser("~") + "\\AppData\\Local\\Stockify"
	mkdir(dataDir)
elif((platform == "linux") or (platform == "linux2")):
	dataDir = "/usr/local/Stockify"
	mkdir(dataDir)
else: # darwin
	dataDir = "/usr/local/bin/Stockify"
	mkdir(dataDir)

move("bins", dataDir)