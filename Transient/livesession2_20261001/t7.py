import json
from bx import call
from st_sandswim_lib import spawn
OUT={}
def log(k, v):
    OUT[k] = v; print(k, json.dumps(v, default=str)[:900], flush=True)
    json.dump(OUT, open("t7.json", "w"), indent=1, default=str)
M="RM_Muurrok86469"
log("list", call("jawa/pawn_use_verb", {"pawn": M, "action": "list"}, 60))
mus, _ = spawn("Muffalo", 186, 73, "none", 3)
log("muffalo", mus)
for i, t in enumerate(mus):
    r = call("jawa/pawn_use_verb", {"pawn": M, "action": "cast", "verb": "mirror crest", "targetId": t}, 120)
    log(f"cast{i}", r)
ps = call("jawa/list_pawns", {"limit": 500, "includeHealth": True}).get("pawns") or []
log("muffalo_hp", [(p["id"], p.get("dead"), [h.get("def") for h in (p.get("health") or {}).get("hediffs", [])]) for p in ps if p["id"] in mus])
log("weather_set", call("jawa/weather_set", {"weather": "Sandstorm"}, 60))
call("rimworld/step_game_ticks", {"ticks": 30}, 60)
mus2, _ = spawn("Muffalo", 186, 76, "none", 1)
r = call("jawa/pawn_use_verb", {"pawn": M, "action": "cast", "verb": "mirror crest", "targetId": mus2[0]}, 120)
log("cast_sandstorm", r)
ps = call("jawa/list_pawns", {"limit": 500, "includeHealth": True}).get("pawns") or []
log("muffalo2_hp", [(p["id"], [h.get("def") for h in (p.get("health") or {}).get("hediffs", [])]) for p in ps if p["id"] in mus2])
