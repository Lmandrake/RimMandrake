import json
from bx import call
rows=[]
for i in range(25):
    call("rimworld/step_game_ticks", {"ticks": 4}, 60)
    fr = call("jawa/pawn_flight", {"action": "report", "kind": "RM_Soorrak"}, 60)
    rs = fr.get("pawns") or fr.get("results") or []
    rows.append([(r["pawn"], r.get("curJobDef"), r.get("x"), r.get("z"), r.get("flightState")) for r in rs])
json.dump(rows, open("t2.json","w"), indent=1)
for r in rows[::4]: print(r)
p = call("jawa/pawn_get", {"pawn": "RM_Soorrak86084"}, 30)["pawns"][0]
print([h.get("def") for h in p.get("hediffs") or []], {n.get("def") if isinstance(n,dict) else n: (n.get("level") if isinstance(n,dict) else None) for n in (p.get("needs") or [])})
print(call("jawa/inspect_string", {"thingId": "RM_Soorrak86084"}, 30))
