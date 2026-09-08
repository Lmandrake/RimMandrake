import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb

tag = str(int(time.time()))
with rb() as b:
    b.call("rimworld/set_camera_zoom_extension", {"enabled": True})
    b.call("jawa/clear_ui", {"all": True})
    b.call("jawa/screenshot_mode", {"enabled": True})
    b.call("rimworld/jump_camera_to_cell", {"x": 103, "z": 122})
    b.call("rimworld/set_camera_zoom", {"rootSize": 65})
    print("CAM", json.dumps(b.call("rimworld/get_camera_state", {}).get("viewRect")))
    r = b.call("jawa/take_screenshot", {"fileName": "sbA_" + tag})
    print("A:", json.dumps({k: v for k, v in r.items() if k != "operation"}))
    b.call("rimworld/jump_camera_to_cell", {"x": 38, "z": 68})
    b.call("rimworld/set_camera_zoom", {"rootSize": 12})
    r = b.call("jawa/take_screenshot", {"fileName": "sbB_" + tag})
    print("B:", json.dumps({k: v for k, v in r.items() if k != "operation"}))
