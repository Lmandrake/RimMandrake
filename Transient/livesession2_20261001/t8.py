import json
from bx import call
from st_sandswim_lib import spawn
OUT={}
def log(k, v):
    OUT[k] = v; print(k, json.dumps(v, default=str)[:700], flush=True)
    json.dump(OUT, open("t8.json", "w"), indent=1, default=str)
M="RM_Muurrok86469"
log("weather_set", call("jawa/weather_set", {"weather": "Clear"}, 60).get("after"))
call("rimworld/step_game_ticks", {"ticks": 30}, 60)
log("w", call("jawa/weather_get", {}, 30).get("weather"))
p = call("jawa/pawn_use_verb", {"pawn": M, "action": "list"}, 60)["result"]
log("pos", (p["pawn"]["position"], [ (v["label"], v["usableByCaster"]) for v in p["verbs"]]))
x, z = p["pawn"]["position"]["x"], p["pawn"]["position"]["z"]
mus, _ = spawn("Muffalo", x + 8, z, "none", 3)
def hp(ids):
    ps = call("jawa/list_pawns", {"limit": 600, "includeHealth": True, "includeCorpses": True}).get("pawns") or []
    return [(q["id"], q.get("dead"), [h.get("def") for h in (q.get("health") or {}).get("hediffs", [])]) for q in ps if q["id"] in ids]
log("pre", hp(mus))
for i, t in enumerate(mus):
    r = call("jawa/pawn_use_verb", {"pawn": M, "action": "cast", "verb": "mirror crest", "targetId": t, "waitTicks": 300} if False else {"pawn": M, "action": "cast", "verb": "mirror crest", "targetId": t}, 120)
    log(f"cast{i}", {k: r.get(k) for k in ("success", "accepted", "refusedBy", "message")})
    call("rimworld/step_game_ticks", {"ticks": 200}, 60)
log("post", hp(mus))
