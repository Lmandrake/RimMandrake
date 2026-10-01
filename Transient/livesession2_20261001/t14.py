import json
from bx import call
from st_sandswim_lib import spawn, paint
def pawns(): return call("jawa/list_pawns", {"limit": 700, "includeHealth": True, "includeCorpses": True}).get("pawns") or []
def hs(pid): return [[h.get("def") for h in (p.get("health") or {}).get("hediffs", [])] for p in pawns() if p["id"] == pid]
print("paint", paint(60, 195, 30, 12, "Gravel"), call("jawa/set_roof_batch", {"rect": "60,195,30,12", "roof": "none"}, 60).get("success") if False else "")
tgt, _ = spawn("Muffalo", 64, 200, "none", 3)
for t in tgt: print("down", call("jawa/pawn_force_incapacitate", {"pawn": t, "action": "downed"}, 60).get("success"))
mu, msg = spawn("RM_Muurrok", 76, 200, "none", 1); print("muurrok", mu, msg)
M = mu[0]
print("w", call("jawa/weather_get", {}, 30)["weather"]["current"])
res = []
for t in tgt:
    b = hs(t)
    r = call("jawa/pawn_use_verb", {"pawn": M, "action": "cast", "verb": "mirror crest", "targetId": t}, 120)
    call("rimworld/step_game_ticks", {"ticks": 150}, 60)
    a = hs(t)
    print("cast", t, r.get("accepted"), r.get("refusedBy"), "\n  before", b, "\n  after ", a)
    res.append((t, r.get("accepted"), b, a))
json.dump(res, open("t14.json", "w"), default=str)
