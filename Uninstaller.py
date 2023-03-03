from os import removedirs, system
from sys import platform

for itr in open("Dependencies/requirements.txt", "r").readlines():
	if itr == "lxml==4.9.2":
		continue

	system(f"python -m pip uninstall {itr}")

if platform == "win32":
	from os.path import expanduser

	usr = expanduser("~")
	removedirs(usr + "\\AppData\\Local\\Stockify")
	removedirs(usr + "\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\src\\lxml")
elif((platform == "linux") or (platform == "linux2")):
	removedirs("/usr/local/Stockify")
	removedirs("/usr/lib/python3/dist-packages/src/lxml")
else: # darwin
	removedirs("/usr/local/bin/Stockify")