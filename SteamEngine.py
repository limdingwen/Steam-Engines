import urllib.request
import urllib.parse
import wptools
import json
import traceback
from bs4 import BeautifulSoup

header = {
    "User-Agent": "SteamEngine/1.0 (https://SteamEngine.com; SteamEngine@SteamEngine.com)"
    }

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

# Problem: Not all apps
# Problem: Fuzzy search can lead to wrong pages (FIXABLE TODO?)
# Problem: Engine might be corrupted (FIXABLE TODO)
def wikipedia(steamapp):
    # steamapp is app name.

    search_url = "https://en.wikipedia.org/w/api.php"

    # Default
    engine = None

    try:
        # Search so Wikipedia can find us the correct page
        # Using fuzzy search terms like "<GAME NAME> video game"
        searchterm = steamapp + " video game"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": searchterm,
            #"srwhat": "nearmatch",
            "srlimit": 1,
            "srprop": "",
            "formatversion": 2,
            "format": "json"
        }
        url = search_url + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(
            url,
            headers = header
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
    except Exception as e:
        debugstacktrace(e)

    return engine

# Problem: Not all apps
# Problem: Only certain engines can be recognized
# Problem: Some games might lead to false negatives like PUBG
# Experimental; more accurate version
def steamdb(steamapp):
    # steamapp is steam ID.

    engine = None

    # Get html
    try:
        depot_id = int(steamapp) + 1
        depot_url = "https://steamdb.info/depot/" + str(depot_id)
        req = urllib.request.Request(
            depot_url,
            headers = header
            )
        response = urllib.request.urlopen(req).read()

        # Get correct Javascript file
        html = BeautifulSoup(response, "html.parser")
        # Without Javascript, the filelist is stored inside
        # the following script tag upon load. <script nonce></script>
        # Might change in the future.
        filelist = html.select("script[nonce]")[0].text

        # Check for engines
        if "UnityEngine.dll" in filelist:
            engine = "Unity"
        if ".uasset" in filelist:
            engine = "Unreal"
    except Exception as e:
        debugstacktrace(e)
        
    return engine

# Problem: Not all apps
# Problem: Fuzzy search can lead to wrong pages (solved with nearmatch?)
def pcgaming(steamapp):
    # steamapp is steam name.

    search_url = "https://pcgamingwiki.com/w/api.php"

    engine = None

    try:
        # Search so PCGamingWiki can find us the correct page
        searchterm = steamapp
        params = {
            "action": "query",
            "list": "search",
            "srsearch": searchterm,
            "srwhat": "nearmatch",
            "srlimit": 1,
            "srprop": "",
            "formatversion": 2,
            "format": "json"
        }
        url = search_url + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(
            url,
            headers = header
            )
        
        retries = 0
        while True:
            try:
                response = urllib.request.urlopen(req).read()
                pagename = json.loads(response)["query"]["search"][0]["title"]
                break
            except Exception as e:
                if retries <= 0:
                    raise e
                else:
                    traceback.print_tb(e.__traceback__)
                retries -= 1

        # Fetch actual page
        page_url = "https://pcgamingwiki.com/wiki/" + urllib.parse.quote(pagename)
        req = urllib.request.Request(
            page_url,
            headers = header
            )
        response = str(urllib.request.urlopen(req).read())

        # Find engine
        # engine_str is absuing the title="Engine:Unity" property
        # in PCGamingWiki generated HTML
        engine_str = "title=\"Engine:"
        if engine_str in response:
            engine = find_between(response, engine_str, "\"")
            if engine == "":
                engine = None
    except Exception as e:
        debugstacktrace(e)

    return engine

def research_engine(steamid, steamname):
    source = "SteamDB"
    debugprint("Steamdb...")
    engine = steamdb(steamid)
    if (engine is None):
        source = "PC Gaming Wiki"
        debugprint("PCGamingWiki...")
        engine = pcgaming(steamname)
    if (engine is None):
        source = "Wikipedia"
        debugprint("Wikipedia...")
        engine = wikipedia(steamname)
    if (engine is None):
        source = "Unavaliable"
        debugprint("No sources returned a valid result.")
        engine = "Unknown"
    return engine, source

def debugstacktrace(e):
    if __name__ == "__main__":
        traceback.print_tb(e.__traceback__)

def debugprint(msg):
    if __name__ == "__main__":
        print(msg)

if __name__ == "__main__":
    steamid = input("What game's engine do you want to know? (ID) ")
    steamname = input("What game's engine do you want to know? (Name) ")
    print(research_engine(steamid, steamname))
    #print(pcgaming(steamname))
