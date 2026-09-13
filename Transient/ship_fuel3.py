import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    roots = rb.call("rimworld/list_debug_action_roots", {})
    print("roots:", str(roots)[:300])
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions"}).get("children", [])
    tnodes = sorted(c["path"] for c in ch if c["path"].split("\\")[-1].startswith("T:"))
    print(len(tnodes), "T: tools; sample:", tnodes[:25])
