import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
for pid,k in [("AA_RedGoo669881","AA_RedGoo"),("AA_RedSpore669921","AA_RedSpore")]:
    p=(S.call("jawa/pawn_get", pawn=pid).get("pawns") or [None])[0]
    if not p: print(pid,"gone"); continue
    x,z=p["position"]["x"],p["position"]["z"]
    rect="%d,%d,9,9"%(x-4,z-4)
    f0=len(S.call("jawa/list_things", defName="Filth_SpentAcid", rect=rect).get("things") or [])
    for i in range(12):
        S.call("jawa/damage", damageDef="Crush", amount=5000, thingId=pid)
        if not (S.call("jawa/pawn_get", pawn=pid).get("pawns")): break
    S.run(30)
    f1=len(S.call("jawa/list_things", defName="Filth_SpentAcid", rect=rect).get("things") or [])
    corpse=len(S.call("jawa/list_things", defName="Corpse_"+k, rect=rect).get("things") or [])
    print("KILL2",k,"at",x,z,"hits",i+1,"corpse",corpse,"acidfilth",f0,"->",f1)
