import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    res = rb.call("rimworld/spawn_thing", {"defName": "VFES_Turret_Artillery", "x": 120, "z": 120})
    print("resp:", json.dumps({k: v for k, v in res.items() if k != "operation"})[:500])
    op = res.get("operation", {})
    print("op warnings:", op.get("Warnings"), "| error:", op.get("Error"))
    tid = res.get("thingId")
    c = rb.call("rimworld/get_cell_info", {"x": 120, "z": 120})
    print("cell things:", [t.get("defName") for t in c.get("things", [])], "| terrain:", c.get("terrainDefName") or c.get("terrain"))
    if tid:
        ti = rb.call("rimworld/get_map_target_info", {"thingId": tid})
        print("target info:", json.dumps({k: v for k, v in ti.items() if k != "operation"})[:300])
