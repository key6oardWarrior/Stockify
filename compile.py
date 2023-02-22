from os import walk, system
from os.path import join

# compile main dir
dirTree: tuple = next(walk("."))[1]
system("py -m compileall -b")

# compile sub dirs
for itr in dirTree:
	system(f"cd {itr} && py -m compileall -b")

# compile unit test
dirTree: list = [join("UnitTest", "DataBase"), join("UnitTest", "Helper"),
	join("UnitTest", "Login")]

for itr in dirTree:
	system(f"cd {itr} && py -m compileall -b")