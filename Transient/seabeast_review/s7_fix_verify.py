import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb, CREATURES, stage_positions, grid_label, STAGES

P = r"D:\Luke\dev\Rimworld\Transient\seabeast_review\placed.json"
d = json.load(open(P))
placed, fails = d["placed"], d["fails"]
have = {(p["x"], p["z"]) for p in placed}

with rb() as b:
    still = []
    for f in fails:
        kind, stage, x, z = f[0], f[1], f[2], f[3]
        i = [j for j, c in enumerate(CREATURES) if c[0] == kind][0]
        s = STAGES.index(stage)
        ok = False
        for dz in (0, -2, 2, -4, 4):
            for dx in (0, -1, 1):
                if ok:
                    break
                tx, tz = x + dx, z + dz
                if (tx, tz) in have:
                    continue
                sp = b.call("jawa/spawn_pawn", {"kindDef": kind, "x": tx, "z": tz,
                                                "faction": "none", "count": 1})
                pl = sp.get("pawns") or []
                if sp.get("success") and pl:
                    p = pl[0]
                    ag = b.call("jawa/set_pawn_age", {"pawn": p["id"],
                                                      "biologicalYears": CREATURES[i][2][s],
                                                      "allowBackwards": True})
                    placed.append({
                        "grid": grid_label(i), "kind": kind, "family": CREATURES[i][3],
                        "stage": stage, "drawSize": CREATURES[i][1][s],
                        "targetAgeYears": CREATURES[i][2][s], "pawnId": p["id"],
                        "x": tx, "z": tz, "reqX": x, "reqZ": z,
                        "lifeStageAfter": (ag.get("after") or {}).get("lifeStage"),
                        "ageAfter": (ag.get("after") or {}).get("biologicalYears"),
                        "ageOk": ag.get("success"), "retriedAt": [tx, tz],
                    })
                    have.add((tx, tz))
                    ok = True
                    print("RETRY OK", kind, stage, "at", tx, tz)
                else:
                    print("  retry fail at", tx, tz, str(sp.get("message"))[:60])
            if ok:
                break
        if not ok:
            still.append(f)
    b.call("jawa/map_commit", {})

with rb() as b:
    lp = b.call("jawa/list_pawns", {"limit": 500})
rows = lp.get("pawns", [])
sea = [r for r in rows if str(r.get("kindDef", "")).startswith("RSW_")]
print("list_pawns:", lp.get("message"), "| RSW pawns:", len(sea))
bykey = {(r["x"], r["z"]): r for r in sea}
for p in placed:
    r = bykey.get((p["x"], p["z"]))
    p["liveKind"] = r.get("kindDef") if r else None
    p["liveBodySize"] = r.get("bodySize") if r else None
    p["kindMatch"] = (p["liveKind"] == p["kind"])
placed.sort(key=lambda p: (p["grid"], STAGES.index(p["stage"])))
json.dump({"placed": placed, "fails": still}, open(P, "w"), indent=1)

bad = [p for p in placed if not p["kindMatch"]]
print("total placed:", len(placed), "| kind mismatches:", len(bad), "| unresolved:", len(still))
for p in bad[:10]:
    print("  MISMATCH", p["grid"], p["stage"], p["kind"], "->", p["liveKind"])
from collections import Counter
print(Counter(p["lifeStageAfter"] for p in placed))
for p in placed[:9]:
    print(" ", p["grid"], p["stage"], p["kind"], "draw", p["drawSize"], "bodySize", p["liveBodySize"], p["lifeStageAfter"])
