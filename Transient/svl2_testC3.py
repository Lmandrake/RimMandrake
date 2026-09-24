import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    cols = rb.call("rimworld/list_colonists", {"currentMapOnly": True})
    for c in cols.get("colonists", []):
        print("COL", c.get("name"), "job=", c.get("job"), "drafted=", c.get("drafted"))
