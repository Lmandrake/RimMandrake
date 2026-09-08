import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=20) as rb:
    rb.call("jawa/clear_ui", {})
    rb.call("rimworld/jump_camera_to_cell", {"x": 115, "z": 117}) if False else None
    r = rb.call("rimworld/take_screenshot", {"fileName": "graffiti_vandal_marks_fixed_2026-09-06"})
    print(json.dumps(r)[:300])
