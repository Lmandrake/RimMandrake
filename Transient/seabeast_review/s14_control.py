import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb

tag = str(int(time.time()))
with rb() as b:
    lp = b.call("jawa/list_pawns", {"limit": 500})
    rows = lp.get("pawns", [])
    sea = [r for r in rows if str(r.get("kindDef", "")).startswith("RSW_")]
    other = [r for r in rows if not str(r.get("kindDef", "")).startswith("RSW_")]
    print("total", len(rows), "sea", len(sea), "other", len(other))
    s0 = sea[0]
    print("sea[0]:", json.dumps(s0))
    print("other[0]:", json.dumps(other[0]))
    # control: a non-sea pawn
    o = other[0]
    b.call("jawa/clear_ui", {})
    b.call("rimworld/jump_camera_to_cell", {"x": o["x"], "z": o["z"]})
    b.call("rimworld/set_camera_zoom", {"rootSize": 12})
    r = b.call("jawa/take_screenshot", {"fileName": "ctl_other_" + tag})
    print("CTRL other at", o["x"], o["z"], o["kindDef"], r.get("fileName"))
    # subject: the biggest adult, Lanternwhale adult at 175,68
    b.call("rimworld/jump_camera_to_cell", {"x": 175, "z": 68})
    b.call("rimworld/set_camera_zoom", {"rootSize": 12})
    r = b.call("jawa/take_screenshot", {"fileName": "ctl_whale_" + tag})
    print("WHALE", r.get("fileName"))
    # what is at 140,119 (the blob centre)?
    print("blob cell:", json.dumps(b.call("rimworld/get_cell_info", {"x": 140, "z": 119})["cell"]))
    print("things near blob:", json.dumps(b.call("jawa/list_things", {"rect": "110,90,60,60", "limit": 30, "includePawns": True}))[:800])
