from os import mkdir, system
from shutil import copytree, move
from sys import platform

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
	pyPackages = usr + "\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\"
	copytree(pyPackages + "lxml", pyPackages + "src\\lxml")
elif((platform == "linux") or (platform == "linux2")):
	# create Stockify dir
	dataDir = "/usr/local/Stockify"
	mkdir(dataDir)

	# create a needed missing directory
	pyPackages = "/usr/lib/python3/dist-packages/"
	copytree(pyPackages + "lxml", pyPackages + "src/lxml")
else: # darwin
	# create Stockify dir
	dataDir = "/usr/local/bin/Stockify"
	mkdir(dataDir)

	# create a needed missing directory

move("bins", dataDir)