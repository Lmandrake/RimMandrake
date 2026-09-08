import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb, STAGES

P = r"D:\Luke\dev\Rimworld\Transient\seabeast_review\placed.json"
placed = json.load(open(P))

with rb() as b:
    lp = b.call("jawa/list_pawns", {"limit": 500})
    sea = {(p["x"], p["z"]): p["kindDef"] for p in lp["pawns"] if str(p.get("kindDef", "")).startswith("RSW_")}
    print("RSW on map:", len(sea))
    bad = [p for p in placed if sea.get((p["x"], p["z"])) != p["kind"]]
    print("position/kind mismatches:", len(bad), bad[:3])
    st = b.call("rimworld/get_cell_info", {"x": 100, "z": 104})["state"]
    print("paused:", st["paused"], st["timeSpeed"])
    r = b.call("rimworld/save_game", {"saveName": "SEABEAST_FAMILIES_20260903"})
    print("SAVE:", json.dumps({k: v for k, v in r.items() if k != "operation"})[:300])
