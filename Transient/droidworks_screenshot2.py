import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

with RimBridge(host, port, token) as rb:
    rb.call("jawa/clear_ui", {})
    rb.call("rimworld/set_camera_zoom", {"rootSize": 8})
    rb.call("rimworld/jump_camera_to_cell", {"x": 50, "z": 40})
    time.sleep(1)
    r = rb.call("rimworld/take_screenshot", {"fileName": "droidworks_minimal_zoom_a.png"})
    print(json.dumps(r.get("path")))

    rb.call("jawa/clear_ui", {})
    rb.call("rimworld/jump_camera_to_cell", {"x": 66, "z": 44})
    time.sleep(1)
    r2 = rb.call("rimworld/take_screenshot", {"fileName": "droidworks_minimal_zoom_b.png"})
    print(json.dumps(r2.get("path")))
