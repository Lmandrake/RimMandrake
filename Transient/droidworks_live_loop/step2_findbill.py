import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions"})
    kids = ch.get("children", [])
    print("root Actions children:", len(kids))
    for c in kids:
        if "bill" in c["path"].lower() or "surgery" in c["path"].lower() or "recipe" in c["path"].lower() or "medical" in c["path"].lower():
            print(c["path"])
