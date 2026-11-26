"""Planted state for the repaired sc_ruins wall-paint row (Pyrelands visit 3): remove the paint from every unowned ruin
Wall on the loaded site (jawa/paint_building removePaint), read back by a census. python.exe, game b, site loaded.
Exit 0 when every unowned wall reads unpainted afterwards, 1 otherwise."""
import json, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h, p, tok = resolve_endpoint()
with RimBridge(h, p, tok) as rb:
    r = rb.call("jawa/list_things", {"group": "BuildingArtificial", "limit": 5000})
    cells = sorted({(x["x"], x["z"]) for x in r.get("things") or [] if x.get("def") == "Wall" and x.get("x") is not None
                    and (x.get("factionName") or x.get("faction")) in (None, "", "None")})
    cs = ";".join("%d,%d" % c for c in cells)
    before = rb.call("jawa/paint_building", {"cells": cs})
    rm = rb.call("jawa/paint_building", {"cells": cs, "removePaint": True})
    after = rb.call("jawa/paint_building", {"cells": cs})
    walls = [x for x in after.get("census") or [] if x.get("def") == "Wall"]
    print(json.dumps({"cells": len(cells), "before": [x for x in before.get("census") or [] if x.get("def") == "Wall"],
                      "removed": rm.get("removed"), "after": walls}))
    sys.exit(0 if walls and all(x.get("color") == "(unpainted)" for x in walls) else 1)
