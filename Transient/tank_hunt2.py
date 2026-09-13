import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for d in ("ChemfuelTank","MinifiedThing"):
        t = rb.call("jawa/list_things", {"defName": d, "limit": 20}).get("things", [])
        print(d, ":", [(x["id"], x["x"], x["z"], x.get("faction")) for x in t])
