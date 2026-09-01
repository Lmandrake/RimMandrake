import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
DESTROY = "Actions" + chr(92) + "T: Destroy"
ok = bad = 0
with RimBridge(host, port, token) as rb:
    for tid in json.load(open(r"D:\Luke\dev\Rimworld\Transient\kill_ids.json")):
        r = rb.call("rimworld/execute_debug_action", {"path": DESTROY, "thingId": "Thing_" + tid})
        ok += 1 if r.get("success") else 0
        bad += 0 if r.get("success") else 1
print("destroyed:", ok, "failed:", bad)
