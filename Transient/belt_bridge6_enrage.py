import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
# PARENTAL_ENRAGE_FACTION_GUARD_1 discriminator: wild calves + wild adult + drafted colonist intruder,
# ProofEnrage read every 125 ticks (per-calf last CompTickRare tick + decision + fresh eval).
K="RSW_ShrublandGiant"
X,Z=int(sys.argv[1]),int(sys.argv[2])
P="RimMandrake.CreatureBehaviors.RM_CompParentalEnrage"
def sp(kind,x,z,fac,n=1):
    r=S.call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=fac, count=n); return [p.get("id") for p in (r.get("pawns") or [])]
def proof(a=""):
    r=S.call("jawa/static_call", type=P, method="ProofEnrage", args=a)
    return r.get("result") if r.get("success") else "CALLFAIL "+json.dumps(r,default=str)[:300]
def cur(pid): return S.call("jawa/pawn_mental", pawn=pid, action="list", limit=1).get("currentState")
print("BEFORE", proof())
calves=sp(K,X,Z,"none",3)
for c in calves: S.call("jawa/set_pawn_age", pawn=c, biologicalYears=0.05, chronologicalYears=0.05, allowBackwards=True)
wild=sp(K,X+7,Z,"none")[0]
col=sp("Colonist",X+1,Z,"player")[0]; S.call("jawa/set_draft", pawnId=col)
print("calves",calves,"wild",wild,"col",col)
for i in range(8):
    S.run(125)
    print("t+%d wild=%s" % ((i+1)*125, cur(wild)))
    if i in (1,3,7):
        for c in calves: print("  ", proof(c).replace("\n"," | "))
print("AFTER", proof().replace("\n"," | ")[:3000])
