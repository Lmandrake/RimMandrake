import sys, time
from collections import Counter
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
from gravship_layout import Layout
lay = Layout.load(r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\GravshipExport\Gravship.xml")
OX, OZ = 142, 58
shipcells = {(OX+x, OZ+z) for z in range(lay.height) for x in range(lay.width) if lay.cell(x, z) and lay.cell(x, z).foundationDef}
ROCK = ("AB_Obsidianstone","SolidMarble","PassableMarble","WeatheredMarble","HewnMarble","BoulderMarble","SolidSandstone","PassableSandstone","WeatheredSandstone","HewnSandstone","BoulderSandstone")
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions"}).get("children", [])
    dest = [c["path"] for c in ch if c["path"].lower().endswith("t: destroy")]
    print("destroy action:", dest)
    P = dest[0]
    r = rb.call("jawa/list_things", {"defName": ",".join(ROCK), "rect": "143,59,86,133", "limit": 9000})
    onship = [t for t in r.get("things", []) if (t["x"], t["z"]) in shipcells]
    print("destroying", len(onship), "rocks...")
    fails = 0
    for t in onship:
        rr = rb.call("rimworld/execute_debug_action", {"path": P, "thingId": t["id"]})
        if not rr.get("success"): fails += 1
    rb.call("jawa/map_commit", {})
    chk = rb.call("jawa/list_things", {"defName": ",".join(ROCK), "rect": "143,59,86,133", "limit": 9000})
    left = [t for t in chk.get("things", []) if (t["x"], t["z"]) in shipcells]
    print("fails:", fails, "| rocks on deck after:", len(left))
