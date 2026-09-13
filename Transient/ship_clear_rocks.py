import sys
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
    r = rb.call("jawa/list_things", {"defName": ",".join(ROCK), "rect": "143,59,86,133", "limit": 9000})
    onship = [t for t in r.get("things", []) if (t["x"], t["z"]) in shipcells]
    print("rocks on deck:", len(onship), Counter(t["def"] for t in onship).most_common(5))
    ids = [t["id"] for t in onship]
    for i in range(0, len(ids), 300):
        d = rb.call("jawa/destroy_batch", {"thingIds": ",".join(ids[i:i+300])})
        assert d.get("success") is True, d
    rb.call("jawa/map_commit", {})
    chk = rb.call("jawa/list_things", {"defName": ",".join(ROCK), "rect": "143,59,86,133", "limit": 9000})
    left = [t for t in chk.get("things", []) if (t["x"], t["z"]) in shipcells]
    print("rocks on deck after:", len(left))
