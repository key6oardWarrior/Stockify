from pip._internal import main
from os.path import join, expanduser
from sys import path, platform
from wget import download

from Installer import createPath

for itr in open(join(join(f"{path[0]}", "Dependencies"), "requirements.txt"),
	"r").readlines():

	main(["install", itr])

if platform == "win32":
	download("https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-6.0.4-signed.msi")
elif((platform == "linux") or (platform == "linux2")):
	download("https://repo.mongodb.org/apt/debian/dists/bullseye/mongodb-org/6.0/main/binary-amd64/mongodb-org-server_6.0.4_amd64.deb")
else: # darwin
	download("https://fastdl.mongodb.org/osx/mongodb-macos-x86_64-6.0.4.tgz")
	download("https://fastdl.mongodb.org/osx/mongodb-macos-arm64-6.0.4.tgz")

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