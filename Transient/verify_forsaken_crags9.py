"""Read glow at Skarnix positions via 'T: Glow At Position' debug action."""
import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

SPOTS = [(220, 220), (215, 222), (210, 225)]

with RimBridge(host, port, token) as rb:
    for (x, z) in SPOTS:
        r = rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: Glow At Position", "x": x, "z": z})
        print(x, z, "->", json.dumps(r)[:800])
