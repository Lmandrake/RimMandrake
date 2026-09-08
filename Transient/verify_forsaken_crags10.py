"""Full response dump for T: Glow At Position."""
import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

with RimBridge(host, port, token) as rb:
    r = rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: Glow At Position", "x": 220, "z": 220})
    print(json.dumps(r, indent=2))
