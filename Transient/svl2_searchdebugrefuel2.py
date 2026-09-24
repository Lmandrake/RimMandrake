import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions"})
    kids = ch.get("children", [])
    print("TOTAL", len(kids))
    for k in kids:
        lbl = k.get("label","").lower()
        if any(w in lbl for w in ["fill", "top up", "topup", "give item", "spawn item", "t:"]):
            print(k.get("path"))
