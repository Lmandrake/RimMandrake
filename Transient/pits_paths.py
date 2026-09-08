import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=20) as rb:
    roots = rb.call("rimworld/list_debug_action_roots", {})
    print("ROOTS", json.dumps(roots)[:500])
    actions_path = None
    for c in roots.get("roots", roots.get("children", [])):
        if c.get("label") == "Actions" or c.get("path") == "Actions":
            actions_path = c["path"]
    print("actions_path", actions_path)
    kids = rb.call("rimworld/list_debug_action_children", {"path": actions_path or "Actions"})
    cats = kids.get("children", [])
    print("num top categories:", len(cats))
    rmpits = [c for c in cats if "RMPits" in c.get("path","") or "RMPits" in c.get("label","")]
    print("RMPits node:", json.dumps(rmpits)[:1000])
