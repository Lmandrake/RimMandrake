import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("jawa/clear_ui", {})
    rb.call("rimworld/jump_camera_to_cell", {"x": 75, "z": 78})
    rb.call("rimworld/set_camera_zoom", {"rootSize": 12})
    res = rb.call("rimworld/take_screenshot", {"fileName": "desert_inject_long_crossing_zoom_2026-09-06"})
    print(res.get("path") or res)
