from os import removedirs, system
from sys import platform
from os.path import join, expanduser

def getAlias() -> str:
	if system("py") == 0:
		return "py"

	if system("py3") == 0:
		return "py3"

	if system("python") == 0:
		return "python"

	if system("python3") == 0:
		return "python3"

if platform == "win32":
	# create Stockify dir
	usr = expanduser("~")
	dataDir = usr + "\\AppData\\Local\\Stockify"
	# create a needed missing directory
	pyPackages = usr + "\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages"
elif((platform == "linux") or (platform == "linux2")):
	# create Stockify dir
	dataDir = "/usr/local/Stockify"
	# create a needed missing directory
	pyPackages = "/usr/lib/python3/dist-packages"
else: # darwin
	# create Stockify dir
	dataDir = "/usr/local/bin/Stockify"
	# create a needed missing directory
	pyPackages = ""

alias = getAlias()

for itr in open(join(dataDir, "Dependencies/requirements.txt", "r")).readlines():
	if itr == "lxml==4.9.2":
		continue

	extCode: int = system(f"{alias} -m pip uninstall {itr}")

removedirs(dataDir)