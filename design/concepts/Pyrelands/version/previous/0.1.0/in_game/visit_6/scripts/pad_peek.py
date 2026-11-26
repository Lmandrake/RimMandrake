"""python.exe: what stands on a rect (things by def) and the roof/terrain of its cells. Visit 6 diagnosis."""
import sys, json, collections
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h, p, tk = resolve_endpoint()
with RimBridge(h, p, tk) as rb:
    for r in sys.argv[1:]:
        ex = rb.call("jawa/export_things", {"rect": r, "includePawns": False, "includeItems": True, "limit": 5000})
        print(r, "things:", dict(collections.Counter(str(t.get("def")) for t in ex.get("things") or [])))
        x, z, w, hh = (int(v) for v in r.split(","))
        ci = rb.call("rimworld/get_cells_info", {"x": x, "z": z, "width": w, "height": hh})
        cells = ci.get("cells") or []
        print("  cells", len(cells), "roof:", dict(collections.Counter(str(c.get("roof") or c.get("roofDef")) for c in cells)),
              "keys:", sorted((cells[0] or {}).keys())[:20] if cells else None)
