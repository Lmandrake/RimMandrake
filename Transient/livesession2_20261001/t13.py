import json, math
from bx import call
from st_sandswim_lib import spawn
def pawns(): return call("jawa/list_pawns", {"limit": 600, "includeHealth": True, "includeCorpses": True}).get("pawns") or []
th = call("jawa/list_things", {"group": "Filth", "limit": 5000})
print("rm_filth", [(t.get("def"), t.get("x"), t.get("z")) for t in th.get("things") or [] if str(t.get("def")).startswith("RM_Filth")])
print("leviathans", [(p["id"], p.get("x"), p.get("z")) for p in pawns() if p.get("kindDef") in ("RM_Muurrok", "RSW_KraytDragon")])
ps = pawns()
tg = [p for p in ps if p.get("isPlayer") and p.get("downed") and not p.get("dead")]
print("downed", [(t["id"], t["x"], t["z"]) for t in tg])
t = tg[0]
ids, msg = spawn("RM_Muurrok", t["x"] + 10, t["z"], "none", 1); print("spawned", ids, msg)
M = ids[0]
def hs(pid): return [[h.get("def") for h in (p.get("health") or {}).get("hediffs", [])] for p in pawns() if p["id"] == pid]
print("muurrok hediffs", hs(M))
for k in range(3):
    b = hs(t["id"])
    r = call("jawa/pawn_use_verb", {"pawn": M, "action": "cast", "verb": "mirror crest", "targetId": t["id"]}, 120)
    print("cast", r.get("accepted"), r.get("refusedBy"), r.get("ticksElapsed"))
    call("rimworld/step_game_ticks", {"ticks": 150}, 60)
    print("before", b, "\nafter ", hs(t["id"]))
