import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb

tag = str(int(time.time()))
with rb() as b:
    sp = b.call("jawa/spawn_pawn", {"kindDef": "RSW_Lanternwhale", "x": 140, "z": 119,
                                    "faction": "none", "count": 1})
    print("SPAWN:", json.dumps({k: v for k, v in sp.items() if k != "operation"})[:400])
    b.call("jawa/clear_ui", {})
    b.call("jawa/screenshot_mode", {"enabled": True})
    b.call("rimworld/jump_camera_to_cell", {"x": 140, "z": 119})
    b.call("rimworld/set_camera_zoom", {"rootSize": 12})
    r = b.call("jawa/take_screenshot", {"fileName": "bright_whale_" + tag})
    print("SHOT", r.get("fileName"))
