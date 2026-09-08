import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=20) as rb:
    roots = rb.call("rimworld/list_debug_action_roots", {})
    for r in roots["roots"]:
        print(r["path"], r.get("label"), r.get("childCount"))
