import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for dn in ["Wall", "Door", "TableTrader", "Bed", "Shelf"]:
        r = rb.call("jawa/list_things", {"rect": "0,0,100,100", "limit": 50, "defName": dn})
        things = r.get("things", [])
        print(dn, "countMatched=", r.get("countMatched"), "returned=", len(things))
        if things:
            xs = [t.get("x") for t in things]
            zs = [t.get("z") for t in things]
            print("  x range", min(xs), max(xs), "z range", min(zs), max(zs))
