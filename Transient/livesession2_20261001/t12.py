import json, math
from bx import call
M="RM_Muurrok86469"
def pawns(): return call("jawa/list_pawns", {"limit": 600, "includeHealth": True, "includeCorpses": True}).get("pawns") or []
def hs(pid): return [[h.get("def") for h in (p.get("health") or {}).get("hediffs", [])] for p in pawns() if p["id"] == pid]
ps = pawns(); m = [p for p in ps if p["id"] == M][0]
tg = [p for p in ps if p.get("isPlayer") and p.get("downed") and not p.get("dead") and 5 <= math.hypot(p["x"]-m["x"], p["z"]-m["z"]) <= 20]
print("muurrok", m["x"], m["z"], "targets", [(t["id"], t["x"], t["z"]) for t in tg])
w = call("jawa/weather_get", {}, 30)["weather"]["current"]; print("weather", w)
for t in tg[:2]:
    b = hs(t["id"])
    r = call("jawa/pawn_use_verb", {"pawn": M, "action": "cast", "verb": "mirror crest", "targetId": t["id"]}, 120)
    print("cast", t["id"], r.get("accepted"), r.get("refusedBy"))
    call("rimworld/step_game_ticks", {"ticks": 200}, 60)
    print("before", b, "\nafter ", hs(t["id"]))
