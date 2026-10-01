import json
from bx import call
from st_sandswim_lib import spawn
M="RM_Muurrok86469"
def pawns():
    return call("jawa/list_pawns", {"limit": 600, "includeHealth": True, "includeCorpses": True}).get("pawns") or []
res=[]
for attempt in range(4):
    m = [p for p in pawns() if p["id"] == M][0]
    ids, msg = spawn("Muffalo", m["x"] + 9, m["z"], "none", 1)
    if not ids: ids, msg = spawn("Muffalo", m["x"] - 9, m["z"], "none", 1)
    t = ids[0]
    r = call("jawa/pawn_use_verb", {"pawn": M, "action": "cast", "verb": "mirror crest", "targetId": t}, 120)
    print("cast", t, (m["x"], m["z"]), r.get("accepted"), r.get("refusedBy"), json.dumps({k: v for k, v in r.items() if k not in ("preCast",)}, default=str)[:400])
    if r.get("accepted"):
        call("rimworld/step_game_ticks", {"ticks": 240}, 60)
        after = [(p.get("dead"), [h.get("def") for h in (p.get("health") or {}).get("hediffs", [])]) for p in pawns() if p["id"] == t]
        print("hp", t, after); res.append((t, after))
json.dump(res, open("t10.json","w"), default=str)
