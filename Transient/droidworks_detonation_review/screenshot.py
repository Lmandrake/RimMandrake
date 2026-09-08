import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("jawa/clear_ui", {})
    shot = rb.call("rimworld/screenshot_cell_rect", {
        "x": 35, "z": 35, "width": 60, "height": 85, "paddingCells": 4, "rootSize": 48,
        "fileName": "droidworks_detonation_review_grid_2026-09-08"})
    print("screenshot:", json.dumps(shot))
