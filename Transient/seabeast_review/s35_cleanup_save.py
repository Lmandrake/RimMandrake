import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb, CREATURES, stage_positions, grid_label, STAGES

P = r"D:\Luke\dev\Rimworld\Transient\seabeast_review\placed.json"
placed = json.load(open(P))["placed"]
want = {(p["x"], p["z"]): (p["kind"], p["stage"], p["grid"]) for p in placed}
print("expected grid cells:", len(want))

with rb() as b:
    # 1. remove the loose slag chunks (Item category) around row A
    r = b.call("jawa/destroy_batch", {"rects": "90,28,25,8", "categories": "Item"})
    print("chunks:", json.dumps({k: v for k, v in r.items() if k != "operation"})[:200])
    # 2. census and kill anything that is not one of the 54
    lp = b.call("jawa/list_pawns", {"limit": 500})
    strays = []
    for p in lp["pawns"]:
        k = str(p.get("kindDef", ""))
        pos = (p["x"], p["z"])
        if k.startswith("RSW_"):
            if pos not in want or want[pos][0] != k:
                strays.append((k, pos))
        elif k == "Muffalo" and abs(p["z"] - 38) < 4 and abs(p["x"] - 100) < 6:
            strays.append((k, pos))
    print("strays:", strays)
    for k, (x, z) in strays:
        b.call("jawa/clear_area", {"rect": "%d,%d,1,1" % (x, z), "dryRun": False})
    b.call("jawa/map_commit", {})

with rb() as b:
    lp = b.call("jawa/list_pawns", {"limit": 500})
    sea = [p for p in lp["pawns"] if str(p.get("kindDef", "")).startswith("RSW_")]
    got = {(p["x"], p["z"]): p["kindDef"] for p in sea}
    missing = [(v, k) for k, v in want.items() if got.get(k) != v[0]]
    extra = [(v, k) for k, v in got.items() if k not in want]
    print("RSW now:", len(sea), "missing:", missing, "extra:", extra)
    r = b.call("rimworld/save_game", {"saveName": "SEABEAST_FAMILIES_20260903"})
    print("SAVE:", json.dumps({k: v for k, v in r.items() if k != "operation"})[:400])
