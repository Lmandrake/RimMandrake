import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions"})
    kids = ch.get("children", [])
    for k in kids:
        if "refuel" in k.get("label","").lower():
            print("HIT", k.get("path"))
    print("root childCount:", ch.get("childCount"), "returned:", len(kids))
