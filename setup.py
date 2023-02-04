from os import system

for itr in open("requirements.txt", "r").readlines():
	if system(f"py -m pip install {itr}") != 0:
		system(f"python -m pip install {itr}")