import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions"})
    kids = [c for c in ch.get("children", []) if c.get("category") == "RimMandrake.Inhabited"]
    for k in kids:
        print(k.get("path"), "|", k.get("label"))
