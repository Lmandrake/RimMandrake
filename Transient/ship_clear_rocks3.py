import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
from gravship_layout import Layout
lay = Layout.load(r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\GravshipExport\Gravship.xml")
OX, OZ = 142, 58
shipcells = {(OX+x, OZ+z) for z in range(lay.height) for x in range(lay.width) if lay.cell(x, z) and lay.cell(x, z).foundationDef}
ROCK = ("AB_Obsidianstone","SolidMarble","PassableMarble","WeatheredMarble","HewnMarble","BoulderMarble","SolidSandstone","PassableSandstone","WeatheredSandstone","HewnSandstone","BoulderSandstone")
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/list_things", {"defName": ",".join(ROCK), "rect": "143,59,86,133", "limit": 9000})
    onship = [t for t in r.get("things", []) if (t["x"], t["z"]) in shipcells]
    # test one with Thing_ prefix
    t0 = onship[0]
    rr = rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: Destroy", "thingId": "Thing_" + t0["id"]})
    print("test:", t0["id"], "->", rr.get("success"), str(rr.get("message",""))[:80])
    if rr.get("success"):
        fails = 0
        for t in onship[1:]:
            r2 = rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: Destroy", "thingId": "Thing_" + t["id"]})
            if not r2.get("success"): fails += 1
        rb.call("jawa/map_commit", {})
        chk = rb.call("jawa/list_things", {"defName": ",".join(ROCK), "rect": "143,59,86,133", "limit": 9000})
        left = [t for t in chk.get("things", []) if (t["x"], t["z"]) in shipcells]
        print("fails:", fails, "| rocks on deck after:", len(left))
