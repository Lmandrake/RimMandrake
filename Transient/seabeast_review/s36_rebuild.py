import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb, CREATURES, stage_positions, grid_label, STAGES

# wipe every RSW pawn left on the map, then rebuild the grid from scratch.
with rb() as b:
    lp = b.call("jawa/list_pawns", {"limit": 500})
    left = [(p["kindDef"], p["x"], p["z"]) for p in lp["pawns"] if str(p.get("kindDef", "")).startswith("RSW_")]
    print("leftover RSW:", left)
    for k, x, z in left:
        b.call("jawa/clear_area", {"rect": "%d,%d,1,1" % (x, z), "dryRun": False})
    lp = b.call("jawa/list_pawns", {"limit": 500})
    print("RSW after wipe:", sum(1 for p in lp["pawns"] if str(p.get("kindDef", "")).startswith("RSW_")))

placed, fails = [], []
with rb() as b:
    for i, (kind, draw, ages, fam) in enumerate(CREATURES):
        for s, (x, z) in enumerate(stage_positions(i)):
            ok = False
            for tx, tz in [(x, z), (x, z - 2), (x, z + 2), (x + 1, z), (x - 1, z)]:
                sp = b.call("jawa/spawn_pawn", {"kindDef": kind, "x": tx, "z": tz,
                                                "faction": "none", "count": 1})
                pl = sp.get("pawns") or []
                if sp.get("success") and pl:
                    p = pl[0]
                    ag = b.call("jawa/set_pawn_age", {"pawn": p["id"], "biologicalYears": ages[s],
                                                      "allowBackwards": True})
                    placed.append({"grid": grid_label(i), "kind": kind, "family": fam,
                                   "stage": STAGES[s], "drawSize": draw[s], "targetAgeYears": ages[s],
                                   "pawnId": p["id"], "x": tx, "z": tz,
                                   "lifeStage": (ag.get("after") or {}).get("lifeStage"),
                                   "ageAfterYears": (ag.get("after") or {}).get("biologicalYears")})
                    ok = True
                    break
            if not ok:
                fails.append((kind, STAGES[s], x, z))
                print("FAIL", kind, STAGES[s], x, z)
    b.call("jawa/map_commit", {})

json.dump(placed, open(r"D:\Luke\dev\Rimworld\Transient\seabeast_review\placed.json", "w"), indent=1)
from collections import Counter
print("placed", len(placed), "fails", len(fails), Counter(p["lifeStage"] for p in placed))
