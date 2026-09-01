import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("jawa/clear_ui", {})
    rb.call("rimworld/jump_camera_to_cell", {"x": 285, "z": 33})
    s = rb.call("rimworld/take_screenshot", {"fileName": "doctrine_kill_20260830"})
    print(s.get("path"))
    rb.call("rimworld/set_time_speed", {"speed": 0})
