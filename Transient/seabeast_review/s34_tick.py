import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb

tag = str(int(time.time()))
with rb() as b:
    r = b.call("rimworld/step_game_ticks", {"ticks": 60})
    print("STEP:", json.dumps({k: v for k, v in r.items() if k != "operation"})[:200])
    b.call("jawa/clear_ui", {})
    b.call("jawa/screenshot_mode", {"enabled": True})
    b.call("rimworld/jump_camera_to_cell", {"x": 100, "z": 32})
    b.call("rimworld/set_camera_zoom", {"rootSize": 12})
    time.sleep(1)
    s = b.call("jawa/take_screenshot", {"fileName": "tick_" + tag})
    print("SHOT", s.get("fileName"))
