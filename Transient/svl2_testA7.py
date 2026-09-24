import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("jawa/clear_ui", {})
    rb.call("rimworld/set_camera_zoom", {"rootSize": 14})
    rb.call("rimworld/jump_camera_to_cell", {"x": 190, "z": 140})
    time.sleep(1.5)
    r3 = rb.call("rimworld/take_screenshot", {"fileName": "svl2_korrum_shot2"})
    print("SCREENSHOT2", json.dumps(r3)[:800])
