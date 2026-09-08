import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb

tag = str(int(time.time()))
with rb() as b:
    print("WEATHER:", json.dumps({k: v for k, v in b.call("jawa/weather_get", {}).items() if k != "operation"})[:600])
    print("CLOCK:", json.dumps({k: v for k, v in b.call("jawa/time_clock", {}).items() if k != "operation"})[:300])
    lp = b.call("jawa/list_pawns", {"rect": "80,20,50,30", "limit": 50})
    print("pawns near A2:", [(p["kindDef"], p["x"], p["z"]) for p in lp["pawns"]])
    b.call("jawa/clear_ui", {})
    b.call("jawa/screenshot_mode", {"enabled": True})
    for nm, x, z, root in [("a2off", 100, 52, 12), ("a2wide", 100, 45, 24)]:
        b.call("rimworld/jump_camera_to_cell", {"x": x, "z": z})
        b.call("rimworld/set_camera_zoom", {"rootSize": root})
        r = b.call("jawa/take_screenshot", {"fileName": "d2_%s_%s" % (nm, tag)})
        print(nm, r.get("fileName"))
