import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=30.0) as rb:
    kids = rb.call("rimworld/list_debug_action_children", {"path": "Actions"})["children"]
    matches = [c["path"] for c in kids if "Report cell" in c.get("path","") or "RAW" in c.get("path","")]
    print("matches:", matches)
    print("total children under Actions:", len(kids))
