import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

SHOTS = [
    ("type1_mechanoid_garrison_v2", 50, 50),
    ("type2_flesh_weapon_loose_v2", 150, 50),
    ("type3_frozen_rakata_v2", 50, 150),
]

with RimBridge(host, port, token) as rb:
    for name, cx, cz in SHOTS:
        rb.call("jawa/clear_ui", {})
        rb.call("rimworld/jump_camera_to_cell", {"x": cx, "z": cz})
        rb.call("rimworld/set_camera_zoom", {"rootSize": 40})
        res = rb.call("rimworld/take_screenshot", {"fileName": f"vault_kcsg_{name}_2026-09-06"})
        print(name, res.get("path") or res)
