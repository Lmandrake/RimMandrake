import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb, CREATURES, stage_positions

x, z = stage_positions(0)[0]
with rb() as b:
    r = b.call("jawa/spawn_pawn", {"kindDef": "RSW_ColoClawFish", "x": x, "z": z, "faction": "none", "count": 1})
    print("SPAWN:", json.dumps(r, indent=1)[:1500])
    pid = (r.get("pawns") or [{}])[0].get("id")
    print("pid", pid)
    a = b.call("jawa/set_pawn_age", {"pawn": pid, "biologicalYears": 0.05, "allowBackwards": True})
    print("AGE:", json.dumps(a, indent=1)[:1200])
    g = b.call("jawa/pawn_get", {"pawn": pid})
    print("GET:", json.dumps(g)[:1500])
