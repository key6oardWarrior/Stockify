from os import removedirs, system
from sys import platform
from os.path import join, expanduser

def _getAlias() -> str:
	if system("py") == 0:
		return "py"

	if system("py3") == 0:
		return "py3"

	if system("python") == 0:
		return "python"

	if system("python3") == 0:
		return "python3"

def uninstall() -> None:
	if platform == "win32":
		# create Stockify dir
		dataDir = expanduser("~") + "\\AppData\\Local\\Stockify"
	elif((platform == "linux") or (platform == "linux2")):
		# create Stockify dir
		dataDir = "/usr/local/Stockify"
	else: # darwin
		# create Stockify dir
		dataDir = "/usr/local/bin/Stockify"

	alias = _getAlias()

	for itr in open(join(dataDir, "Dependencies/requirements.txt", "r")).readlines():
		if itr == "lxml==4.9.2":
			continue

		system(f"{alias} -m pip uninstall {itr}")

	removedirs(dataDir)