import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb

tag = str(int(time.time()))
with rb() as b:
    lp = b.call("jawa/list_pawns", {"limit": 500})
    rows = lp["pawns"]
    sea = [r for r in rows if str(r.get("kindDef", "")).startswith("RSW_")]
    print("total", len(rows), "RSW", len(sea))
    ci = b.call("rimworld/get_cell_info", {"x": 140, "z": 139})
    print("state", json.dumps(ci.get("state"))[:200], "cell fog", ci["cell"]["fogged"])
    b.call("rimworld/set_camera_zoom_extension", {"enabled": True})
    b.call("jawa/clear_ui", {})
    b.call("jawa/screenshot_mode", {"enabled": True})
    for name, x, z, root in [("a2", 100, 32, 12), ("b1", 38, 68, 16), ("ov", 103, 122, 65)]:
        b.call("rimworld/jump_camera_to_cell", {"x": x, "z": z})
        b.call("rimworld/set_camera_zoom", {"rootSize": root})
        r = b.call("jawa/take_screenshot", {"fileName": "post_%s_%s" % (name, tag)})
        print(name, r.get("fileName"))
