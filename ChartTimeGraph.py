import csv
import json
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime

### CREATE EASY TO USE STRUCTURES

notables = [
    "Unity", "Unreal", "CryEngine", "Godot", "Source", "GoldSrc",
    "id Tech", "GameMaker", "Frostbite", "RPG Maker", "Ren'Py", "Fox Engine",
    "Snowdrop", "Fusion", "Adventure Game Studio", "Lumberyard", "Flash"
    ]

inputfilename = "engines.csv"#input("Enter engines.csv file name: ")
engines = {}
with open(inputfilename, newline="", encoding="utf-8") as inputfile:
    gameengines = csv.reader(inputfile)

    next(gameengines)
    for gameengine in gameengines:
        game = gameengine[0]
        engine = gameengine[1]
        engines[game] = engine

inputfilename = "steamapps.txt"#input("Enter steamapps.txt file name: ")
steamapps = []
with open(inputfilename, "rb") as inputfile:
    json = json.load(inputfile)
    for steamapp_json in json["applist"]["apps"]:
        steamapps.append({
            "appid": steamapp_json["appid"],
            "name": steamapp_json["name"]
            })

### COUNT ENGINES PER YEAR

def determine_release_year(appid):
    # Get html
    url = "https://store.steampowered.com/app/" + str(appid)
    req = urllib.request.Request(url)
    try:
        response = urllib.request.urlopen(req).read()
    except:
        return None

    # Parse html
    html = BeautifulSoup(response, "html.parser")
    releasedates = html.select(".release_date .date")
    if len(releasedates) == 0:
        return None
    releasedate = releasedates[0].text
    year = datetime.strptime(releasedate, "%d %b, %Y").year
    
    print(str(appid) + " " + str(year))
    return year

id_intervals = int(input("How many games between each year check? "))
current_year = 2000
ids_left = 0
# [["Year", "Unity", "Unreal"...],[1999,4738,328]]
counts = [["Year"] + notables]
counts_current_year = [current_year] + [0]*len(notables)
for steamapp in steamapps:
    if ids_left <= 0:
        # Update year
        prev_year = current_year
        new_year = determine_release_year(steamapp["appid"])
        if new_year != None:
            current_year = new_year
            ids_left = id_intervals
            if prev_year != current_year:
                counts.append(counts_current_year)
                counts_current_year = [current_year] + [0]*len(notables)

    # Count engine
    engine = engines[steamapp["name"]]
    index = 1
    for notable in notables:
        if notable.lower() in engine.lower():
            counts_current_year[index] += 1
        index += 1

    ids_left -= 1

counts.append(counts_current_year)

### EXPORT

print(counts)
print("Exporting to timechart.csv...")
with open("timechart.csv", "w", newline="") as outfile:
    outwriter = csv.writer(outfile)
    for count in counts:
        outwriter.writerow(count)

    
