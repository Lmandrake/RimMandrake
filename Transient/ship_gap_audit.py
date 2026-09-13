import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
sys.path.insert(0, "src/RimMandrake/Utils".replace("/", "\\") if sys.platform=="win32" else "src/RimMandrake/Utils")
from gravship_layout import Layout
lay = Layout.load(r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\GravshipExport\Gravship.xml")
OX, OZ = 142, 58
want = [(OX+x, OZ+z) for z in range(lay.height) for x in range(lay.width) if lay.cell(x, z) and lay.cell(x, z).foundationDef]
print("expected foundation cells:", len(want))
host, port, token = resolve_endpoint()
missing = []
with RimBridge(host, port, token) as rb:
    # read foundation layer in row batches via get_terrain_layers
    for i in range(0, len(want), 400):
        chunk = want[i:i+400]
        r = rb.call("jawa/get_terrain_layers", {"cells": ";".join(f"{x},{z}" for x,z in chunk)})
        for c in r.get("cells", []):
            if not c.get("foundation"):
                missing.append((c["x"], c["z"]))
print("missing foundation:", len(missing))
print(missing[:50])
json.dump(missing, open(r"D:\Luke\dev\Rimworld\Transient\ship_missing_cells.json", "w"))
