from os import system

for itr in open("requirements.txt", "r").readlines():
	system(f"py -m pip install {itr}")