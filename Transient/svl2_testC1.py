import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/spawn_pawn", {"kindDef": "Colonist", "x": 195, "z": 143, "faction": "PlayerColony"})
    print("SPAWN_CIVILIAN", json.dumps(r)[:1200])
    cols = rb.call("rimworld/list_colonists", {"currentMapOnly": True})
    print("N_COLONISTS_AFTER", len(cols.get("colonists", [])))
    for c in cols.get("colonists", []):
        print("COL", c.get("name"), c.get("job"))
