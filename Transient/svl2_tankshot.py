import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("jawa/clear_ui", {})
    rb.call("rimworld/set_camera_zoom", {"rootSize": 11})
    rb.call("rimworld/jump_camera_to_cell", {"x": 171, "z": 139})
    time.sleep(1.5)
    r3 = rb.call("rimworld/take_screenshot", {"fileName": "svl2_bactatank_shot"})
    print("SCREENSHOT", json.dumps(r3)[:700])
