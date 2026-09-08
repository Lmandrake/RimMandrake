import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb

tag = str(int(time.time()))
with rb() as b:
    r = b.call("jawa/set_fog", {"action": "floodUnfog", "cell": "140,119", "sendLetters": False})
    print("FLOOD:", json.dumps({k: v for k, v in r.items() if k != "operation"})[:300])
    r = b.call("jawa/set_fog", {"action": "unfog", "rect": "0,0,250,250"})
    print("UNFOGRECT:", json.dumps({k: v for k, v in r.items() if k != "operation"})[:300])
    b.call("jawa/map_commit", {"full": True})
    b.call("jawa/clear_ui", {})
    b.call("jawa/screenshot_mode", {"enabled": True})
    b.call("rimworld/jump_camera_to_cell", {"x": 140, "z": 139})
    b.call("rimworld/set_camera_zoom", {"rootSize": 14})
    r2 = b.call("jawa/take_screenshot", {"fileName": "fog2_" + tag})
    print("SHOT", r2.get("fileName"))
