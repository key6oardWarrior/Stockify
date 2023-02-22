from os import mkdir
from os.path import expanduser
from sys import platform
from shutil import move

if platform == "win32":
	dataDir = expanduser("~") + "\\AppData\\Local"
	mkdir(dataDir)
elif((platform == "linux") or (platform == "linux2")):
	dataDir = "/usr/local/Stockify"
	mkdir(dataDir)
else: # darwin
	dataDir = "/usr/local/bin/Stockify"
	mkdir(dataDir)

move("bins", dataDir)