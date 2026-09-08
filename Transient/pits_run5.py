import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=20) as rb:
    node = rb.call("rimworld/get_debug_action", {"path": "Actions\\Spawn Pawn..."})
    print("node:", json.dumps(node, indent=2)[:2500])
