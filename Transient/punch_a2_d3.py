import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
FIX = [("CoastalIsland","239,361,3507,4569"), ("Archipelago","2249,13203"), ("Peninsula","11851")]
with RimBridge(host, port, token) as rb:
    for d, tiles in FIX:
        r = rb.call("jawa/world_mutators_set", {"action": "remove", "mutators": d, "tiles": tiles, "readBack": 1})
        print(d, "->", r.get("success"), r.get("removed", r.get("message","?")))
    a = rb.call("jawa/world_features_set", {"action": "edit", "featureId": 67, "drawAngle": 35})
    print("Scald Spine drawAngle:", a.get("success"))
    rb.call("jawa/world_commit", {})
    # verify removals raw
    m = rb.call("jawa/world_mutators_get", {"tiles": "239,361,3507,4569,2249,13203,11851", "limit": 10})
    for row in m.get("tiles", []):
        bad = [d['def'] for d in row['mutators'] if d['def'] in ('CoastalIsland','Archipelago','Peninsula')]
        print("tile", row['tile'], "coastal-family remaining:", bad)
