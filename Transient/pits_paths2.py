import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=20) as rb:
    kids = rb.call("rimworld/list_debug_action_children", {"path": "Actions"})
    cats = kids.get("children", [])
    labels = [c.get("label") for c in cats]
    hits = [l for l in labels if l and ("pit" in l.lower() or "rm" in l.lower())]
    print("possible hits:", hits)
    print("all labels:", labels)
