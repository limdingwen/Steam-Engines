import json
import wptools
import urllib.request
import urllib.parse
import csv
import time
import datetime
import threading

### FUNCTIONS

def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out

### PARSE STEAM APPS

search_url = "https://en.wikipedia.org/w/api.php"

inputfilename = input("Input Steam file name: ")
inputfile = open(inputfilename, mode="rb")

print("Parsing Steam apps... ", end="")
steamapps_json = json.load(inputfile)
steamapps = []

for steamapp_json in steamapps_json["applist"]["apps"]:
    steamapp = steamapp_json["name"]
    steamapps.append(steamapp)

inputfile.close()

print("Done.")

### GET ENGINES

print("There are " + str(len(steamapps)) + " Steam apps in total.")
limit = int(input("How many do you want to research? (Type 0 for max) "))
if limit == 0:
    limit = len(steamapps)

threadcount = int(input("How many threads do you want to use? "))

print("Make sure to close engines.csv!!!")
print("Researching engines...")

def researchThread(threadapps):
    global appcount
    
    for steamapp in threadapps:
        # Default
        engine = "Unknown"

        try:
            # Search so Wikipedia can find us the correct page
            # Using fuzzy search terms like "<GAME NAME> video game"
            searchterm = steamapp + " video game"
            params = {
                "action": "query",
                "list": "search",
                "srsearch": searchterm,
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
            enginelink_components = enginelink.split("|")
            # Take the last string, not 1, since some might not be links: Engine name
            engine = enginelink_components[-1]
        except:
            pass

        gameengines.append(
            {
                "game": steamapp,
                "engine": engine
                }
            )

        appcount += 1
        current_time = time.time()
        eta_seconds = (current_time - start_time) / appcount * (limit - appcount)
        eta = str(datetime.timedelta(seconds=eta_seconds)).split(".")[0]
        print(str(appcount) + " out of " + str(limit) + " apps researched. ("
              + str(int(appcount/limit*100)) + "%, time remaining " + eta + ")")

gameengines = []
appcount = 0
start_time = time.time()

limitedsteamapps = steamapps[:limit]
threadsapps = chunkIt(limitedsteamapps, threadcount)
threads = []
for threadapps in threadsapps:
    thread = threading.Thread(target=researchThread, args=[threadapps])
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

print("Done.")

### EXPORT TO CSV

print("Exporting to engines.csv... ", end="")

outputfile = open("engines.csv", "w", newline="", encoding="utf-8")
writer = csv.writer(outputfile, delimiter=",")
writer.writerow(["Game", "Engine"])

for gameengine in gameengines:
    writer.writerow([gameengine["game"], gameengine["engine"]])
    
outputfile.close()

print("Done.")
