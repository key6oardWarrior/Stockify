from sys import argv, path, platform

slash = "\\"

if platform != "win32":
	slash = "/"

addedPath = path[0][:path[0].rfind(slash)]
path.append(addedPath[:addedPath.rfind(slash)])
del slash, addedPath

from Helper.helper import getPayment

status: tuple[bool, int] = getPayment(argv[1], argv[2], argv[3], argv[4], argv[5], argv[6], argv[7], argv[8], argv[9], argv[10], False)
assert status == (True, "I00001")

status: tuple[bool, int] = getPayment(argv[1], argv[2], argv[3], argv[4], argv[5], argv[6], argv[7], argv[8], argv[9], argv[10], True)
assert status == (True, "I00001")
print("pass:", status)