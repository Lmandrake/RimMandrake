import json, math
from bx import call
M="RM_Muurrok86469"
def pawns():
    return call("jawa/list_pawns", {"limit": 600, "includeHealth": True, "includeCorpses": True}).get("pawns") or []
res=[]
for attempt in range(6):
    ps = pawns(); m = [p for p in ps if p["id"] == M][0]
    cands = sorted([p for p in ps if not p.get("dead") and p["id"] != M and p.get("kindDef") in ("Muffalo",)], key=lambda p: math.hypot(p["x"]-m["x"], p["z"]-m["z"]))
    cands = [p for p in cands if 5 <= math.hypot(p["x"]-m["x"], p["z"]-m["z"]) <= 20]
    if not cands: print("no cand"); call("rimworld/step_game_ticks", {"ticks": 60}, 60); continue
    t = cands[0]; before = [h.get("def") for h in (t.get("health") or {}).get("hediffs", [])]
    r = call("jawa/pawn_use_verb", {"pawn": M, "action": "cast", "verb": "mirror crest", "targetId": t["id"]}, 120)
    print("cast", t["id"], r.get("accepted"), r.get("refusedBy"), json.dumps({k: v for k, v in r.items() if k not in ("preCast",)}, default=str)[:500])
    if r.get("accepted"):
        call("rimworld/step_game_ticks", {"ticks": 240}, 60)
        after = [[h.get("def") for h in (p.get("health") or {}).get("hediffs", [])] for p in pawns() if p["id"] == t["id"]]
        print("hp", t["id"], before, "->", after); res.append((t["id"], before, after))
        if any(len(a) > len(before) for a in after): break
json.dump(res, open("t9.json","w"), default=str)
