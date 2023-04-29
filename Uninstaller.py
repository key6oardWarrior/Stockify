from os import system
from sys import platform
from os.path import join, expanduser
from shutil import rmtree

def _getAlias() -> str:
	if system("py3 --help") == 0:
		return "py3"

	if system("py --help") == 0:
		return "py"

	if system("python --help") == 0:
		return "python"

	if system("python3 --help") == 0:
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

	for itr in open(join(dataDir, "Dependencies/requirements.txt"), "r").readlines():
		if itr == "lxml==4.9.2":
			continue

		system(f"echo Y | {alias} -m pip uninstall {itr}")

	rmtree(dataDir, True)