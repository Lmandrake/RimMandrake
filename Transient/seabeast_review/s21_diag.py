import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb

with rb() as b:
    for x, z in [(140, 139), (103, 145), (140, 119), (160, 150)]:
        ci = b.call("rimworld/get_cell_info", {"x": x, "z": z})["cell"]
        print(x, z, "terr", ci["terrainDefName"], "roof", ci["roofDefName"], "fog", ci["fogged"],
              "things", ci["thingCount"], ci["things"])
    lt = b.call("jawa/list_things", {"rect": "115,115,60,60", "limit": 200, "includePawns": True})
    print("countMatched", lt.get("countMatched"), "n", len(lt.get("things", [])))
    for t in lt.get("things", [])[:25]:
        print("   ", t["def"], t["x"], t["z"])
