import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb

with rb() as b:
    r = b.call("jawa/clear_area", {"rect": "128,116,24,7", "dryRun": False})
    print("CLEAR strays destroyed:", r.get("destroyedCount"),
          [d["def"] for d in r.get("destroyed", [])][:12])
    lt = b.call("jawa/list_things", {"rect": "115,110,60,20", "limit": 50, "includePawns": True})
    print("left in strip:", lt.get("countMatched"), [(t["def"], t["x"], t["z"]) for t in lt.get("things", [])])
    lp = b.call("jawa/list_pawns", {"limit": 500})
    sea = [p for p in lp["pawns"] if str(p.get("kindDef", "")).startswith("RSW_")]
    print("RSW pawns now:", len(sea))
    b.call("jawa/map_commit", {"full": True})
with rb() as b:
    r = b.call("rimworld/save_game", {"saveName": "SEABEAST_FAMILIES_20260903"})
    print("SAVE:", json.dumps({k: v for k, v in r.items() if k != "operation"})[:600])
