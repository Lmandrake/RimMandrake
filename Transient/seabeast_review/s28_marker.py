import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb

tag = str(int(time.time()))
with rb() as b:
    r = b.call("jawa/spawn_batch", {"ops": "ChunkSlagSteel:100,32;ChunkSlagSteel:96,32;ChunkSlagSteel:105,32"})
    print("MARKERS:", json.dumps({k: v for k, v in r.items() if k != "operation"})[:300])
    b.call("jawa/spawn_pawn", {"kindDef": "Muffalo", "x": 100, "z": 38, "faction": "none", "count": 1})
    b.call("jawa/map_commit", {})
    b.call("jawa/clear_ui", {})
    b.call("jawa/screenshot_mode", {"enabled": True})
    b.call("rimworld/jump_camera_to_cell", {"x": 100, "z": 35})
    b.call("rimworld/set_camera_zoom", {"rootSize": 12})
    time.sleep(1)
    r = b.call("jawa/take_screenshot", {"fileName": "mark_" + tag})
    print("SHOT", r.get("fileName"))
