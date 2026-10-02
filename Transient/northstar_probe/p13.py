import sys, json
sys.path.insert(0, "src/RimMandrake/Utils"); sys.path.insert(0, "src/RimMandrake/Utils/modcheck")
from rimdrive.session import Session
def fires(s): return s.call("jawa/list_things", defName="Fire")["countMatched"]
with Session(strict=False, quiet=True, focus=False) as s:
    print("fires at start", fires(s))
    r=s.call("jawa/spawn_pawn", kindDef="Boomalope", x=60, z=60, faction="none"); a=r["pawns"][0]["id"]; print("spawned", a)
    r=s.call("jawa/spawn_pawn", kindDef="Boomalope", x=90, z=60, faction="none"); b=r["pawns"][0]["id"]
    s.call("jawa/pawn_force_incapacitate", pawn=a, action="kill"); print("fires after KILL boomalope:", fires(s))
    s.call("jawa/map_fire", action="extinguish", rect="0,0,250,250")
    r=s.call("jawa/destroy_bulk", filter="factionlessAnimals", dryRun=True); r.pop("operation",None); print("destroy_bulk dry:", json.dumps(r)[:300])
    r=s.call("jawa/destroy_bulk", filter="factionlessAnimals", dryRun=False); r.pop("operation",None); print("destroy_bulk real:", json.dumps(r)[:300])
    print("fires after DESTROY:", fires(s))
    rows=[x for x in s.call("jawa/list_pawns", limit=500, includeCorpses=True)["pawns"] if x["id"] in (a,b)]
    print("rows:", [(x["id"], x["dead"], x["spawned"]) for x in rows])
    s.call("jawa/map_fire", action="extinguish", rect="0,0,250,250")
