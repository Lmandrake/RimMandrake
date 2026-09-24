import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions", "includeHidden": True})
    kids = ch.get("children", [])
    print("total", len(kids))
    for k in kids:
        lbl = k.get("label","").lower()
        if "refuel" in lbl or "fuel" in lbl:
            print(k.get("path"), "|", k.get("actionType"))
