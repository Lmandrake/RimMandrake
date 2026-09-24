import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    cols = rb.call("rimworld/list_colonists", {"currentMapOnly": True})
    for c in cols.get("colonists", []):
        if c.get("name") == "Rachel":
            print("RACHEL", json.dumps(c)[:800])
    insp = rb.call("jawa/inspect_string", {"thing": "RSW_BactaTank692523"})
    print("TANK_INSPECT", json.dumps(insp)[:1000])
