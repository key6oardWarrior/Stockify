from os import system
from os.path import join
from sys import path, platform
from wget import download

for itr in open(join(join(f"{path[0]}", "Dependencies"), "requirements.txt"),
	"r").readlines():

	system(f"python -m pip install {itr}")

if platform == "win32":
	download("https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-6.0.4-signed.msi")
elif((platform == "linux") or (platform == "linux2")):
	download("https://repo.mongodb.org/apt/debian/dists/bullseye/mongodb-org/6.0/main/binary-amd64/mongodb-org-server_6.0.4_amd64.deb")
	download("https://repo.mongodb.org/apt/debian/dists/bullseye/mongodb-org/6.0/main/binary-amd64/mongodb-org-mongos_6.0.4_amd64.deb")
else: # darwin
	download("https://fastdl.mongodb.org/osx/mongodb-macos-x86_64-6.0.4.tgz")
	download("https://fastdl.mongodb.org/osx/mongodb-macos-arm64-6.0.4.tgz")
