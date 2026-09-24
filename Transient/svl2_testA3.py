import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/clear_ui", {})
    print("CLEAR_UI", json.dumps(r)[:500])
    r2 = rb.call("rimworld/jump_camera_to_cell", {"x": 230, "z": 230})
    print("JUMP_CAM", json.dumps(r2)[:800])
    r3 = rb.call("rimworld/take_screenshot", {"path": "Transient/svl2_korrum_shot.png"})
    print("SCREENSHOT", json.dumps(r3)[:1500])
