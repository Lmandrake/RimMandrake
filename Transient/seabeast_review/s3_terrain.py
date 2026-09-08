import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb

RECT = "12,12,196,220"

with rb() as b:
    r = b.call("jawa/clear_area", {"rect": RECT, "dryRun": False})
    print("CLEAR:", json.dumps(r)[:500])
with rb() as b:
    r = b.call("jawa/set_terrain_batch", {"ops": "Sand:12,12,196,220", "layer": "top", "refresh": True})
    print("TERRAIN:", json.dumps(r)[:500])
with rb() as b:
    r = b.call("jawa/map_commit", {})
    print("COMMIT:", json.dumps(r)[:300])
    for (x, z) in [(20, 20), (100, 120), (180, 200), (38, 32)]:
        ci = b.call("rimworld/get_cell_info", {"x": x, "z": z})["cell"]
        print("  readback", x, z, ci["terrainDefName"], "walkable", ci["walkable"], "things", ci["thingCount"])
