import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb, CREATURES, stage_positions, grid_label, STAGES

# 1. wipe anything already standing in the grid area (incl. the probe pawn)
with rb() as b:
    r = b.call("jawa/clear_area", {"rect": "12,12,196,220", "dryRun": False})
    print("CLEAR destroyed", r.get("destroyedCount"))

placed = []
fails = []
with rb() as b:
    for i, (kind, draw, ages, fam) in enumerate(CREATURES):
        for s, (x, z) in enumerate(stage_positions(i)):
            sp = b.call("jawa/spawn_pawn", {"kindDef": kind, "x": x, "z": z,
                                            "faction": "none", "count": 1})
            pl = sp.get("pawns") or []
            if not sp.get("success") or not pl:
                fails.append((kind, STAGES[s], x, z, sp.get("message")))
                print("FAIL", kind, STAGES[s], json.dumps(sp)[:200])
                continue
            p = pl[0]
            pid = p["id"]
            ag = b.call("jawa/set_pawn_age", {"pawn": pid,
                                              "biologicalYears": ages[s],
                                              "allowBackwards": True})
            placed.append({
                "grid": grid_label(i), "kind": kind, "family": fam,
                "stage": STAGES[s], "drawSize": draw[s], "targetAgeYears": ages[s],
                "pawnId": pid, "spawnedKindDef": p.get("kindDef") or p.get("kind"),
                "x": p["position"]["x"] if isinstance(p.get("position"), dict) else x,
                "z": p["position"]["z"] if isinstance(p.get("position"), dict) else z,
                "reqX": x, "reqZ": z,
                "lifeStageAfter": (ag.get("after") or {}).get("lifeStage"),
                "ageAfter": (ag.get("after") or {}).get("biologicalYears"),
                "ageOk": ag.get("success"),
            })
    b.call("jawa/map_commit", {})

json.dump({"placed": placed, "fails": fails},
          open(r"D:\Luke\dev\Rimworld\Transient\seabeast_review\placed.json", "w"), indent=1)
print("placed", len(placed), "fails", len(fails))
bad = [p for p in placed if p["spawnedKindDef"] != p["kind"] or (p["x"], p["z"]) != (p["reqX"], p["reqZ"])]
print("kind-substitutions or displaced:", len(bad))
for p in bad[:20]:
    print("  ", p["grid"], p["kind"], p["spawnedKindDef"], (p["x"], p["z"]), (p["reqX"], p["reqZ"]))
from collections import Counter
print(Counter(p["lifeStageAfter"] for p in placed))
