import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
from gravship_layout import Layout
lay = Layout.load(r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\GravshipExport\Gravship.xml")
OX, OZ = 142, 58
want = {(OX+x, OZ+z) for z in range(lay.height) for x in range(lay.width) if lay.cell(x, z) and lay.cell(x, z).foundationDef}
print("expected foundation cells:", len(want))
host, port, token = resolve_endpoint()
have = set()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/get_terrain_layers", {"rect": "143,59,86,133", "onlyFoundation": True, "limit": 20000})
    for c in r.get("cells", []):
        if c.get("foundation"): have.add((c["x"], c["z"]))
missing = sorted(want - have)
print("missing foundation:", len(missing), missing[:40])
json.dump(missing, open(r"D:\Luke\dev\Rimworld\Transient\ship_missing_cells.json","w"))
# what's standing there?
with RimBridge(host, port, token) as rb:
    for x, z in missing[:12]:
        ci = rb.call("rimworld/get_cell_info", {"x": x, "z": z})
        print((x,z), ci.get("terrainDefName"), [t.get("defName") for t in ci.get("things", [])])
