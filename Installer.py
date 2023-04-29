from os import mkdir, getcwd
from os.path import isdir, join, expanduser
from shutil import copytree, move, rmtree
from sys import platform, path, version_info
from pip._internal import main

from PySimpleGUI import Text, Button, Window

path.append(path[0][:path[0].rfind("\\")])
from Helper.helper import exit, exitApp

def lst2Str(lst: list[str]) -> str:
	'''
	Convert a list to a str

	# Params:
	lst - The string list to be converted to a str

	# Returns:
	A string with all of lst's data
	'''
	string = ""
	for itr in lst:
		string += itr + "\n"

	return string

def fixFile(PATH: str) -> None:
	'''
	Fix one of Python's packages, so it will work for our App

	# Params:
	PATH - The file to be fixed
	'''
	rFile = open(PATH, "r").read().splitlines()
	rFile[806] = "class _PluralBinding (collections.abc.MutableSequence):"
	open(PATH, "w").write(lst2Str(rFile))

def createPath(dataDir: str, pyPackages: str) -> None:
	'''
	Create the needed paths for the app to run

	# Params:
	dataDir - The directory that contains all the App's code\n
	pyPackages - All of Python's packages
	'''
	if isdir(dataDir) == False:
		mkdir(dataDir)

	JOINED_PATH = join(pyPackages, join("src", "lxml"))
	if isdir(JOINED_PATH) == False:
		copytree(join(pyPackages, "lxml"), JOINED_PATH)

	# edit content.py to fix error if error exists
	try:
		from collections import MutableSequence
	except:
		fixFile(join(pyPackages, "pyxb\\binding\\content.py"))

layout: list[list] = []
if version_info.major != 3:
	possible2Continue = False
	layout.append([Text("Your version of Python is not supported :(\nPlease install Python 3.11, or greater. To install Python please click on Python installer")])
elif version_info.minor < 11:
	possible2Continue = True
	layout.append([Text("While it is possible to run this program with your Python version.\nWe recommend downloading the version of Python that came with this installer.")])
	layout.append([Button("Continue Without Updating", button_color="light gray", key="continue"), Button("Exit", key="exit")])

if len(layout) > 0:
	win = Window("Stockify", layout)

	event, values = win.read()
	if possible2Continue:
		if(exitApp(event, win)):
			exit(0)
	else:
		exit(0)

# upgrade pip and install all required dependencies
main(["install", "--upgrade", "pip"])
CWD = getcwd()
for package in open(join(CWD, join(join("Dependencies",
	"requirements.txt"))), "r").readlines():
	main(["install", package])

if platform == "win32":
	# create Stockify dir
	usr = expanduser("~")
	dataDir = usr + "\\AppData\\Local\\Stockify"
	# create a needed missing directory
	pyPackages = usr + "\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages"
	createPath(dataDir, pyPackages)
elif((platform == "linux") or (platform == "linux2")):
	# create Stockify dir
	dataDir = "/usr/local/Stockify"
	# create a needed missing directory
	pyPackages = "/usr/lib/python3/dist-packages"
	createPath(dataDir, pyPackages)
else: # darwin
	# create Stockify dir
	dataDir = "/usr/local/bin/Stockify"
	# create a needed missing directory
	pyPackages = ""
	createPath(dataDir, pyPackages)

if isdir(dataDir):
	rmtree(dataDir, True)

# throws exception for moving bin folder, but dont want it to do that anyway
try:
	move(CWD, dataDir)
except Exception as e:
	pass
