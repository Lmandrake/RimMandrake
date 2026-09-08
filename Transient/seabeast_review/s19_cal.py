import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb

tag = str(int(time.time()))
with rb() as b:
    b.call("jawa/clear_ui", {})
    b.call("jawa/screenshot_mode", {"enabled": True})
    for dz in (0, 12, 20):
        b.call("rimworld/jump_camera_to_cell", {"x": 140, "z": 119 + dz})
        b.call("rimworld/set_camera_zoom", {"rootSize": 14})
        cs = b.call("rimworld/get_camera_state", {})
        r = b.call("jawa/take_screenshot", {"fileName": "cal%d_%s" % (dz, tag)})
        print("dz", dz, "mapPos", json.dumps(cs.get("mapPosition")), r.get("fileName"))
