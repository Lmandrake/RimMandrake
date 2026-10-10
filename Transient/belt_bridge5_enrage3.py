import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
def sp(kind,x,z,fac,n=1):
    r=S.call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=fac, count=n); return [p.get("id") for p in (r.get("pawns") or [])]
a=sp("RSW_ShrublandGiant",100,150,"none")[0]; c=sp("Colonist",104,150,"player")[0]
r=S.call("jawa/pawn_mental", pawn=a, action="start", state="RM_ParentalEnrage", otherPawn=c, limit=1)
print("force start", {k:r.get(k) for k in ("success","started","notes","currentState","message")})
S.run(60); print("after60", S.call("jawa/pawn_mental", pawn=a, action="list", limit=1).get("currentState"))
