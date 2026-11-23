"""python.exe: read terrain ops (and cell info of one cell) over rects given as x,z,w,h args. Visit 6 diagnosis."""
import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h, p, tk = resolve_endpoint()
with RimBridge(h, p, tk) as rb:
    for r in sys.argv[1:]:
        t = rb.call("jawa/get_terrain_batch", {"rects": r})
        print(r, "terrain:", str(t.get("ops"))[:600])
        x, z = (int(v) for v in r.split(",")[:2])
        c = rb.call("rimworld/get_cell_info", {"x": x + 1, "z": z + 1})
        print("  cell", x + 1, z + 1, json.dumps({k: c.get(k) for k in ("terrain", "terrainDefName", "roof", "things", "fertility", "isWater")})[:600])
