import sys, re
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("jawa/destroy_batch", {"rects": "20,250,90,320", "categories": "Plant"})
    c = rb.call("rimworld/spawn_thing", {"defName":"VanometricPowerCell","x":30,"z":260})
    t = rb.call("rimworld/spawn_thing", {"defName":"GTbc_TheSingularityCannon","x":34,"z":262})
    tid = t["thingId"].replace("Thing_","")
    rb.call("jawa/set_thing_props", {"thing": tid, "faction": "PlayerColony"})
    ins = rb.call("jawa/inspect_string", {"thingIds": tid})
    print("cannon:", (ins.get("things") or [{}])[0].get("inspect"))
    r = rb.call("rimworld/execute_debug_action", {"path": "Actions\\Spawn Pawn...\\Megascarab", "x": 60, "z": 290})
    rb.call("jawa/clear_ui", {})
    rb.call("rimworld/jump_camera_to_cell", {"x": 55, "z": 285})
    s1 = rb.call("rimworld/take_screenshot", {"fileName": "singularity_before_20260830"})
    print("before:", s1.get("path"))
