import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb

tag = str(int(time.time()))
with rb() as b:
    ui = b.call("rimworld/get_ui_state", {})
    print("UI:", json.dumps({k: v for k, v in ui.items() if k != "operation"})[:500])
    lay = b.call("rimworld/get_ui_layout", {})
    print("surfaces:", [s.get("type") for s in lay.get("surfaces", [])][:20])
    b.call("jawa/screenshot_mode", {"enabled": False})
    b.call("rimworld/jump_camera_to_cell", {"x": 100, "z": 32})
    b.call("rimworld/set_camera_zoom", {"rootSize": 12})
    r = b.call("rimworld/take_screenshot", {"fileName": "alt_" + tag})
    print("ALT:", json.dumps({k: v for k, v in r.items() if k != "operation"})[:400])
