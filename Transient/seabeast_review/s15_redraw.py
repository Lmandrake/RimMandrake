import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb

tag = str(int(time.time()))
with rb() as b:
    r = b.call("jawa/map_commit", {"full": True})
    print("COMMIT full:", json.dumps({k: v for k, v in r.items() if k != "operation"})[:400])
with rb() as b:
    b.call("jawa/clear_ui", {})
    b.call("jawa/screenshot_mode", {"enabled": True})
    b.call("rimworld/jump_camera_to_cell", {"x": 162, "z": 68})
    b.call("rimworld/set_camera_zoom", {"rootSize": 12})
    r = b.call("jawa/take_screenshot", {"fileName": "chk_whale_" + tag})
    print("WHALE", r.get("fileName"))
