import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    lp = rb.call("jawa/list_pawns", {})
    for p in lp.get("pawns", []):
        if p.get("id") == "Human669116":
            print(json.dumps(p)[:800])
    cols = rb.call("rimworld/list_colonists", {"currentMapOnly": True})
    for c in cols.get("colonists", []):
        if c.get("name") == "The Long Pot":
            print("COL", json.dumps(c)[:800])
