from os import system
from os.path import join
from sys import path, platform

for itr in open(join(join(f"{path[0]}", "Dependencies"), "requirements.txt"),
	"r").readlines():

	system(f"python -m pip install {itr}")
