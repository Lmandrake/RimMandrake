import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

SOAK_PATH = "Actions" + chr(92) + "T: Soak 5x5 here"
CELLS = [15, 17, 19, 21, 23, 25]

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for x in CELLS:
        r = rb.call("rimworld/execute_debug_action", {"path": SOAK_PATH, "x": x, "z": 15})
        print(x, r.get("success"), r.get("message"), (r.get("effects") or {}).get("logs"))
