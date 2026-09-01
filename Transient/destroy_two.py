import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
DESTROY = "Actions" + chr(92) + "T: Destroy"
with RimBridge(host, port, token) as rb:
    for tid in json.load(open(r"D:\Luke\dev\Rimworld\Transient\cut_two_ids.json")):
        r = rb.call("rimworld/execute_debug_action", {"path": DESTROY, "thingId": "Thing_" + tid})
        print(tid, r.get("success"))
