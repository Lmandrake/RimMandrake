import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    z = rb.call("rimworld/set_camera_zoom", {"rootSize": 12})
    print("ZOOM", json.dumps(z)[:500])
    r2 = rb.call("rimworld/jump_camera_to_cell", {"x": 230, "z": 230})
    print("JUMP_CAM", json.dumps(r2)[:400])
    r3 = rb.call("rimworld/take_screenshot", {"fileName": "svl2_korrum_shot"})
    print("SCREENSHOT", json.dumps(r3)[:1500])
