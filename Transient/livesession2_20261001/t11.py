import json
from bx import call
M="RM_Muurrok86469"
for i in range(5):
    p = call("jawa/pawn_use_verb", {"pawn": M, "action": "list"}, 60)["result"]
    v = p["verbs"][0]
    ps = call("jawa/list_pawns", {"limit": 600, "includeHealth": True, "includeCorpses": True}).get("pawns") or []
    mf = [(q["id"], q.get("dead"), q.get("x"), q.get("z"), [h.get("def") for h in (q.get("health") or {}).get("hediffs", [])]) for q in ps if str(q["id"]).startswith("Muffalo865")]
    print(call("rimworld/get_game_info", {}, 30).get("ticksGame"), p["pawn"]["position"], p["pawn"]["currentJob"], v["state"], v.get("warmingUp"), mf)
    call("rimworld/step_game_ticks", {"ticks": 300}, 60)
