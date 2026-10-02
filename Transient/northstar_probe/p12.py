import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from rimdrive.session import Session
with Session(strict=False, quiet=True, focus=False) as s:
    rows=s.call("jawa/list_pawns", includeHealth=True, limit=500)["pawns"]
    for r in rows:
        if r["isPlayer"] and r["intelligence"]=="Humanlike":
            print(r["id"], json.dumps(r["health"]["hediffs"]))
    r=s.call("jawa/pawn_health", pawn="Human619", action="remove", hediff="Gunshot", bodyPart="Leg"); r.pop("operation",None); print("remove Gunshot/Leg ->", json.dumps(r)[:300])
    r=s.call("jawa/pawn_health", pawn="Human619", action="remove", hediff="Gunshot"); r.pop("operation",None); print("remove Gunshot (no part) ->", json.dumps(r)[:300])
