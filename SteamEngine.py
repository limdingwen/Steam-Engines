import urllib.request
import urllib.parse
import wptools
import json
import traceback
from bs4 import BeautifulSoup
import queue
import threading
#import mwparserfromhell

header = {
    "User-Agent": "SteamEngine/1.0 (https://SteamEngine.com; SteamEngine@SteamEngine.com)"
    }

# {"PCGaming Wiki": 1000}
requestcounters = {}

def reset_request_counters():
    requestcounters = {}

def countreqs(source, reqs = 1):
    if source not in requestcounters:
        requestcounters[source] = 0
    requestcounters[source] += reqs

reset_request_counters()

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

# 2 to 3 requests
# Problem: Not all apps
def wikipedia(steamappfull, killsig):
    source = "Wikipedia"
    
    def get_engine_from_wppage(pagename):
            # Use wptools to parse page and get engine info from infobox
            page = wptools.page(pagename, verbose=False, silent=True)
            
            # Get engine info: [[Engine Wikipedia page|Engine name]]
            # Trim string off: Engine Wikipedia page|Engine name
            #enginelink = page.get_parse().data["infobox"]["engine"][:-2][2:]
            # Split string: "Engine Wikipedia page", "Engine name"
            #enginelink_components = enginelink.split("|")
            # Take the last string, not 1, since some might not be links: Engine name
            #return enginelink_components[-1]

            # Test cases
            
            # Crysis
            # [[CryEngine 2]] {{small|(PC)}} <br>[[CryEngine 3]] {{small|(PS3 & X360)}}
            # Testing complicated
            
            # Cities: Skylines
            # [[Unity (game engine)|Unity]]
            # Testing edited link names
            
            # Star Conflict
            # Hammer Engine
            # Testing no links
            
            engine = page.get_parse().data["infobox"]["engine"]
            debugprint(engine)
            # CryEngine 2]] {{small|(PC)}} <br>[[CryEngine 3]] {{small|(PS3 & X360)}}
            # Unity (game engine)|Unity]]
            # Hammer Engine
            engine = engine.split("[[", 1)[-1]
            # CryEngine 2
            # Unity (game engine)|Unity
            # Hammer Engine
            engine = engine.split("]]")[0]
            # CryEngine 2
            # Unity
            # Hammer Engine
            engine = engine.split("|", 1)[-1]
            return engine
    
    # steamapp is app name.
    steamapp = steamappfull["name"]

    search_url = "https://en.wikipedia.org/w/api.php"

    # Default
    engine = None

    try:
        # Search so Wikipedia can find us the correct page
        # Using fuzzy search terms like "<GAME NAME> video game"
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
        if killsig is True:
            return None, None
        debugprint("Requesting Wikipedia search...")
        countreqs(source)
        response = urllib.request.urlopen(req).read()
        pagename = json.loads(response)["query"]["search"][0]["title"]

        try:
            if killsig is True:
                return None, None
            debugprint("Requesting Wikipedia exact page...")
            countreqs(source)
            engine = get_engine_from_wppage(pagename)
        except Exception as e:
            debugstacktrace(e)
            if killsig is True:
                return None, None
            debugprint("Requesting Wikipedia video game disambiguation page...")
            countreqs(source)
            engine = get_engine_from_wppage(pagename + " (video game)")
            
    except Exception as e:
        debugstacktrace(e)

    return engine, source

# 1 request
# Problem: Not all apps
# Problem: Only certain engines can be recognized
# Problem: Some games might lead to false Unknowns like PUBG
# Experimental; more accurate version
def steamdb(steamappfull, killsig):
    # steamapp is steam ID.
    steamapp = steamappfull["id"]
    
    engine = None
    source = "SteamDB"

    # Get html
    try:
        depot_id = int(steamapp) + 1
        depot_url = "https://steamdb.info/depot/" + str(depot_id)
        req = urllib.request.Request(
            depot_url,
            headers = header
            )
        if killsig is True:
            return None, None
        debugprint("Requesting SteamDB +1 depot page...")
        countreqs(source)
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
        
    return engine, source

# 2 requests
# Problem: Not all apps
def pcgaming(steamappfull, killsig):
    # steamapp is steam name.
    steamapp = steamappfull["name"]

    search_url = "https://pcgamingwiki.com/w/api.php"

    engine = None
    source = "PCGaming Wiki"

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
                if killsig is True:
                    return None, None
                debugprint("Requesting PCGaming Wiki search...")
                countreqs(source)
                response = urllib.request.urlopen(req).read()
                pagename = json.loads(response)["query"]["search"][0]["title"]
                break
            except Exception as e:
                if retries <= 0:
                    raise e
                else:
                    debugstacktrace(e)
                retries -= 1

        # Fetch actual page
        page_url = "https://pcgamingwiki.com/wiki/" + urllib.parse.quote(pagename)
        req = urllib.request.Request(
            page_url,
            headers = header
            )
        if killsig is True:
            return None, None
        debugprint("Requesting PCGaming Wiki page...")
        countreqs(source)
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

    return engine, source

def queue_return(func, args, result_queue):
    result_queue.put(func(*args))

# Prioritize less requests first, to lower spam rate on sources & speed up
# Prioritize better coverage first, to speed up script
# Prioritize more accurate sources first, to raise accuracy
# TODO: Randomization to even "spam"?
def research_engine(steamid, steamname):
    """source = ""
    engine = None
    if (engine is None):
        source = "PC Gaming Wiki"
        debugprint("PCGamingWiki...")
        engine = pcgaming(steamname)
    if (engine is None):
        source = "Wikipedia"
        debugprint("Wikipedia...")
        engine = wikipedia(steamname)
    if (engine is None):
        source = "SteamDB"
        debugprint("Steamdb...")
        engine = steamdb(steamid)
    if (engine is None):
        source = "Unavaliable"
        debugprint("No sources returned a valid result.")
        engine = "Unknown"
    """

    source_funcs = [steamdb, pcgaming, wikipedia]

    # Create a thread for every source
    result_queue = queue.Queue()
    thread_kill_sigs = []
    threadsleft = 0
    for source_func in source_funcs:
        thread_kill_sig = False
        thread = threading.Thread(target=queue_return,
                         args=(source_func, ({
                             "id": steamid,
                             "name": steamname
                             }, lambda: thread_kill_sig), result_queue))
        thread.daemon = True
        thread.start()
        thread_kill_sigs.append(thread_kill_sig)
        threadsleft += 1

    # Wait for first result to come in
    # If valid, then kill all other threads and finish
    # If not, wait for next result
    # Unless it's last thread, in which case, unknown
    while True:
        engine, source = result_queue.get()
        threadsleft -= 1
        if engine is None:
            if threadsleft == 0:
                return "Unavaliable", "Unknown"
        else:
            for thread_kill_sig in thread_kill_sigs:
                thread_kill_sig = True
            return engine, source

def debugstacktrace(e):
    if __name__ == "__main__":
        traceback.print_tb(e.__traceback__)

def debugprint(msg):
    if __name__ == "__main__":
        print(msg + "\n", end="")

if __name__ == "__main__":
    steamid = int(input("What game's engine do you want to know? (ID) "))
    steamname = input("What game's engine do you want to know? (Name) ")
    print(research_engine(steamid, steamname))
    print(requestcounters)
    #print(research_engine(322500, "SUPERHOT"))
    #print(research_engine(578080, "PLAYERUNKNOWN'S BATTLEGROUNDS"))
    #print(wikipedia(steamname))
