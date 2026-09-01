import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions"})["children"]
    tp = [c["path"] for c in ch if "eleport" in c["path"]]
    print("teleport leaves:", tp[:3])
