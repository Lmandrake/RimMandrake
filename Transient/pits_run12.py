import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def logs(r):
    return [l["message"] for l in r.get("effects", {}).get("logs", [])]
with RimBridge(host, port, token, timeout=20) as rb:
    r = rb.call("rimworld/spawn_thing", {"defName": "RM_OpenPit_Oiled", "x": 100, "z": 130})
    print("spawn:", r.get("thingId"), r.get("success"))
    print("ignite:", logs(rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: Oiled: ignite (bypasses soaked/Sprung gate)", "x": 100, "z": 130})))
    r = rb.call("rimworld/get_cell_info", {"x": 100, "z": 130})
    print("cell after:", json.dumps([t["defName"] for t in r["cell"]["things"]]))
