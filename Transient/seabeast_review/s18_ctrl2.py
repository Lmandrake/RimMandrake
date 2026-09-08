import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb

tag = str(int(time.time()))
with rb() as b:
    for kind, x, z in [("Muffalo", 136, 119), ("RSW_ShaleGorger", 144, 119)]:
        sp = b.call("jawa/spawn_pawn", {"kindDef": kind, "x": x, "z": z, "faction": "none", "count": 1})
        print(kind, sp.get("message"))
    print(json.dumps(b.call("jawa/list_pawns", {"rect": "125,110,30,20"}).get("pawns"), indent=0)[:1200])
    b.call("jawa/clear_ui", {})
    b.call("jawa/screenshot_mode", {"enabled": True})
    b.call("rimworld/jump_camera_to_cell", {"x": 140, "z": 119})
    b.call("rimworld/set_camera_zoom", {"rootSize": 14})
    r = b.call("jawa/take_screenshot", {"fileName": "ctrl2_" + tag})
    print("SHOT", r.get("fileName"))
