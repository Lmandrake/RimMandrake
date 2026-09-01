import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions"})["children"]
    dest = [c["path"] for c in ch if c["path"].split(chr(92))[-1] in ("T: Destroy", "T: Destroy...")]
    print("destroy node:", dest)
    if dest:
        r = rb.call("rimworld/execute_debug_action", {"path": dest[0], "thingId": "Thing_VFES_Turret_Artillery359602"})
        print("destroy:", r.get("success"), str(r.get("message",""))[:80])
        ti = rb.call("rimworld/get_map_target_info", {"thingId": "Thing_VFES_Turret_Artillery359602"})
        print("still exists?:", ti.get("success"), str(ti.get("message",""))[:60])
