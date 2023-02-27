from os import mkdir, system
from shutil import move
from sys import platform
from shutil import copytree

system(f"python -m pip install --upgrade pip")
for itr in open("Dependencies/requirements.txt", "r").readlines():
	system(f"python -m pip install {itr}")

if platform == "win32":
	from os.path import expanduser

	# create Stockify dir
	usr = expanduser("~")
	dataDir = usr + "\\AppData\\Local\\Stockify"
	mkdir(dataDir)

	# create a needed missing directory
	pyPackages = usr + "AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\"
	mkdir(pyPackages + "src")
	copytree(pyPackages + "lxml", pyPackages + "src")
elif((platform == "linux") or (platform == "linux2")):
	# create Stockify dir
	dataDir = "/usr/local/Stockify"
	mkdir(dataDir)

	# create a needed missing directory
else: # darwin
	# create Stockify dir
	dataDir = "/usr/local/bin/Stockify"
	mkdir(dataDir)

	# create a needed missing directory

move("bins", dataDir)