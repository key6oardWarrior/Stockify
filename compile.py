from os import walk, system, mkdir, rename, remove
from os.path import join, isdir, exists
from shutil import copy2, move

# compile main dir
system("py -m compileall -b")

dirTree: tuple = next(walk("."))
testTree: list = [join("UnitTest", "DataBase"), join("UnitTest", "Helper"),
	join("UnitTest", "Login")]

if isdir("bins") == False:
	mkdir("bins")

# compile sub dirs
for itr in dirTree[1]:
	system(f"cd {itr} && py -m compileall -b")

	# copy all compiled (non-unit test) files into bins folder
	if((itr != ".git") and (itr != "bins") and (itr != ".vscode") and
		(itr != "UnitTest")):
		dirName = join("bins", itr)

		if isdir(dirName) == False:
			mkdir(dirName)

		for file in next(walk(itr))[2]:
			if file[-4:] == ".pyc":
				copy2(join(itr, file), dirName)

# copy main compiled files to bins folder
for itr in dirTree[2]:
	if itr[-4:] == ".pyc":
		if((itr != "compile.pyc") and (itr != "setup.pyc")):
			copy2(itr, "bins")

# compile unit test
for itr in testTree:
	system(f"cd {itr} && py -m compileall -b")

# convert the main .pyc file to a .pyw
PATH = join("UI", "Stockify.py")
FINAL_PATH = join("bins", PATH + "w")

if exists(FINAL_PATH):
	remove(FINAL_PATH)

copy2(join("Dependencies", "requirements.txt"), join("bins", "Dependencies"))
rename(join("bins", PATH + "c"), FINAL_PATH)
move(FINAL_PATH, "Stockify.pyw")
