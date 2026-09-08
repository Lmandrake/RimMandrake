"""Jump camera to a Skarnix, clear UI, screenshot -- check ambient light by eye."""
import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

with RimBridge(host, port, token) as rb:
    rb.call("jawa/clear_ui", {})
    r = rb.call("rimworld/jump_camera_to_cell", {"x": 220, "z": 220})
    print("jump", r.get("success"))
    shot = rb.call("rimworld/take_screenshot", {"fileName": "forsaken_crags_ambient_check.png"})
    print("screenshot:", json.dumps(shot)[:500])
