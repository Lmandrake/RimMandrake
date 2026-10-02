import sys; sys.path.insert(0,"Transient")
from cp_lib import *
r = call("jawa/spawn_pawn", kindDef="Rat", x=200, z=40, faction="none", count=1); rid = r["pawns"][0]["id"]; print("rat", rid)
before = call("jawa/damage_log", action="status")["totalRecorded"]
d = call("jawa/damage", damageDef="Cut", amount=3, thingId=rid); print("damage:", J(d,300))
l = call("jawa/damage_log", action="read", thingId=rid); print("after hit: matched", l["matchedCount"], [(e["seq"],e["kind"],e["damageDef"],e["amount"],e["instigatorId"],e["hitPart"],e["victimDeadAfter"]) for e in l["events"]])
k = call("jawa/pawn_force_incapacitate", pawn=rid, action="kill"); print("kill:", J(k,300))
l = call("jawa/damage_log", action="read", thingId=rid); print("after kill: matched", l["matchedCount"], [(e["seq"],e["kind"],e["damageDef"],e["amount"],e["culpritHediff"],e["victimDeadAfter"]) for e in l["events"]])
print("total delta", call("jawa/damage_log", action="status")["totalRecorded"]-before)
