import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

SHOTS = [
    ("waste_camp_v3", 85, 40, 26),
    ("boneyard_v5", 132, 87, 30),
    ("long_crossing_v5", 170, 38, 28),
]

with RimBridge(host, port, token) as rb:
    for name, cx, cz, zoom in SHOTS:
        rb.call("jawa/clear_ui", {})
        rb.call("rimworld/jump_camera_to_cell", {"x": cx, "z": cz})
        rb.call("rimworld/set_camera_zoom", {"rootSize": zoom})
        res = rb.call("rimworld/take_screenshot", {"fileName": f"desert_inject_{name}_2026-09-06"})
        print(name, res.get("path") or res)
