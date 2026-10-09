import sys; sys.path.insert(0,"Transient")
from belt_lc6_lib import *
kind="RM_GreatboleGrub"
print(call("jawa/get_defs", defs="PawnKindDef/"+kind, fields="defName").get("notFound"))
calves=[spawn_pawn(kind,190,60,"none",1)["pawns"][0]["id"] for _ in range(3)]
adult=spawn_pawn(kind,196,60,"none",1)["pawns"][0]["id"]
for c in calves: show(call("jawa/set_pawn_age", pawn=c, biologicalYears=0.0, chronologicalYears=0.0),80)
show(call("jawa/set_pawn_age", pawn=adult, biologicalYears=3, chronologicalYears=3),80)
json.dump({"calves":calves,"adult":adult},open("Transient/belt_lc6_h.json","w"))
print(calves, adult)
