import urllib.request

print("Getting all steam apps...")
steamapps = urllib.request\
    .urlopen("https://api.steampowered.com/ISteamApps/GetAppList/v2/")\
    .read()
print("Done.")

filename = input("Export file name: ")
file = open(filename, "wb")
file.write(steamapps)
print("Done.")
