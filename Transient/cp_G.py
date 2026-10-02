import sys; sys.path.insert(0,"Transient")
from cp_lib import *
r = call("jawa/pawn_roles")
from collections import Counter
for p in r["pawns"]:
    if p["kindDef"] in ("Horse","Colonist","Emu"):
        print(p["id"], p["kindDef"], "faction", p["faction"], "isPlayer", p["isPlayer"], "isColonist", p["isColonist"], "isFree", p["isFreeColonist"], "isAnimal", p["isAnimal"], "controlled", p["isColonistPlayerControlled"])
print("colonists by isColonist:", sum(1 for p in r["pawns"] if p["isColonist"]), "isPlayer:", sum(1 for p in r["pawns"] if p["isPlayer"]), "total", r["count"])
bad = call("jawa/pawn_roles", ids="Human960,NoSuchPawn123"); print("unresolved id ->", J({k:bad.get(k) for k in ("success","message")},300))
bad = call("jawa/pawn_census", ids="NoSuchPawn123"); print("census unresolved ->", J({k:bad.get(k) for k in ("success","message")},300))
print("faction=player census:", call("jawa/pawn_census", faction="player")["count"])
