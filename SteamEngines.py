import json
import wptools
import urllib.request
import urllib.parse

search_url = "https://en.wikipedia.org/w/api.php"

#inputfilename = input("Input Steam file name: ")
#inputfile = open(inputfilename, mode="rb")

#print("Parsing file...")
#steamapps = json.load(inputfile)

print("Searching Wikipedia...")

# Search so Wikipedia can find us the correct page
# Using fuzzy search terms like "<GAME NAME> video game"
params = {
    "action": "query",
    "list": "search",
    "srsearch": "Totally Accurate Battlegrounds video game",
    "srlimit": 1,
    "srprop": "",
    "formatversion": 2,
    "format": "json"
}
url = search_url + "?" + urllib.parse.urlencode(params)
req = urllib.request.Request(
    url,
    headers = {
        "User-Agent": "SteamEngine/1.0 (https://SteamEngine.com; SteamEngine@SteamEngine.com)"
        }
    )
response = urllib.request.urlopen(req).read()
pagename = json.loads(response)["query"]["search"][0]["title"]

# Use wptools to parse page and get engine info from infobox
page = wptools.page(pagename, verbose=False, silent=True)
# Get engine info: [[Engine Wikipedia page|Engine name]]
# Trim string off: Engine Wikipedia page|Engine name
enginelink = page.get_parse().data["infobox"]["engine"][:-2][2:]
# Split string: "Engine Wikipedia page", "Engine name"
enginelinkcomponents = enginelink.split("|")
# Take the last string, not 1, since some might not be links: Engine name
engine = enginelinkcomponents[-1]
print(engine)
