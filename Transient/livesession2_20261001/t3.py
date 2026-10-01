import json
from bx import call
rows=[]
for i in range(12):
    call("rimworld/step_game_ticks", {"ticks": 7}, 60)
    out=[]
    for k in ("RM_Soorrak","RM_Oorrik","RM_Vekka"):
        fr = call("jawa/pawn_flight", {"action": "report", "kind": k}, 60)
        out += [(r["pawn"], r.get("curJobDef"), r.get("x"), r.get("z")) for r in (fr.get("pawns") or [])]
    rows.append(out)
json.dump(rows, open("t3.json","w"), indent=1)
for r in rows[::3]: print(r)
for pid in ("RM_Soorrak86084","RM_Soorrak86085","RM_Oorrik86078"):
    p = call("jawa/pawn_get", {"pawn": pid}, 30)["pawns"][0]
    print(pid, [(h.get("def"), h.get("severity")) for h in p.get("hediffs") or []])
