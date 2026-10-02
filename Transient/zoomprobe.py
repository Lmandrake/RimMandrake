#!/usr/bin/env python3
"""Read-only zoom threshold probe for SHULLA_INVISIBLE_RENDER_1 (re-scoped).
No spawning, no saving, no unpausing. Camera + screenshot only.
Run with python.exe from WSL.
"""
import sys, os, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
rb = RimBridge(host=host, port=port, token=token).connect()

cx, cz = 99, 17
print("game info:", rb.call("rimworld/get_game_info", {}))
print("cam before:", rb.call("rimworld/get_camera_state", {}))

for n in (11, 12, 13, 14):
    rb.call("jawa/clear_ui", {})
    rb.call("rimworld/jump_camera_to_cell", {"x": cx, "z": cz})
    rb.call("rimworld/set_camera_zoom", {"rootSize": float(n)})
    time.sleep(0.5)
    cam = rb.call("rimworld/get_camera_state", {})
    print(f"rootSize req={n} actual={cam.get('rootSize')}")
    r = rb.call("rimworld/take_screenshot", {"fileName": f"zoomprobe_{n}", "suppressMessage": True})
    print("  shot:", r.get("path"))
    time.sleep(0.3)

print("cam after:", rb.call("rimworld/get_camera_state", {}))
