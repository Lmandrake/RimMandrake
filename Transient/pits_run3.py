import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=20) as rb:
    r = rb.call("rimworld/execute_debug_action", {"path": "Actions\\Add Prisoner"})
    print(json.dumps(r, indent=2))
