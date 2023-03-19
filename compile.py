from os import walk, system, mkdir, rename, remove
from os.path import join, isdir, exists
from shutil import copy2, move

# compile main dir
system("py -m compileall -b")

dirTree: tuple = next(walk("."))
testTree: list = [join("UnitTest", "DataBase"), join("UnitTest", "Helper"),
	join("UnitTest", "Login")]

if isdir("App") == False:
	mkdir("App")

# compile sub dirs
for itr in dirTree[1]:
	system(f"cd {itr} && py -m compileall -b")

	# copy all compiled (non-unit test) files into App folder
	if((itr != ".git") and (itr != "App") and (itr != ".vscode") and
		(itr != "UnitTest")):
		dirName = join("App", itr)

		if isdir(dirName) == False:
			mkdir(dirName)

		for file in next(walk(itr))[2]:
			if file[-4:] == ".pyc":
				copy2(join(itr, file), dirName)

# copy main compiled files to App folder
for itr in dirTree[2]:
	if itr[-4:] == ".pyc":
		if((itr != "compile.pyc") and (itr != "setup.pyc")):
			copy2(itr, "App")

# compile unit test
for itr in testTree:
	system(f"cd {itr} && py -m compileall -b")

# convert the main .pyc file to a .pyw
PATH = join("UI", "Stockify.py")
FINAL_PATH = join("App", PATH + "w")

if exists(FINAL_PATH):
	remove(FINAL_PATH)

copy2(join("Dependencies", "requirements.txt"), join("App", "Dependencies"))
rename(join("App", PATH + "c"), FINAL_PATH)
move(FINAL_PATH, "Stockify.pyw")