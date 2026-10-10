import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
# PARENTAL_ENRAGE_FACTION_GUARD_1 A1 with fine polling (the rage lasts <125 ticks once the intruder is bitten
# and leaves the 10-cell disengage radius, so bridge5's 125-tick poll could not see it).
K="RSW_ShrublandGiant"
P="RimMandrake.CreatureBehaviors.RM_CompParentalEnrage"
def sp(kind,x,z,fac,n=1):
    r=S.call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=fac, count=n); return [p.get("id") for p in (r.get("pawns") or [])]
def cur(pid): return S.call("jawa/pawn_mental", pawn=pid, action="list", limit=1).get("currentState")
def scene(name,X,Z,calfFac):
    calves=sp(K,X,Z,calfFac,3)
    for c in calves: S.call("jawa/set_pawn_age", pawn=c, biologicalYears=0.05, chronologicalYears=0.05, allowBackwards=True)
    wild=sp(K,X+7,Z,"none")[0]; tame=sp(K,X-7,Z,"player")[0]
    col=sp("Colonist",X+1,Z,"player")[0]
    print(name,"calves",calves,"wild",wild,"tame",tame,"col",col)
    seen={"wild":set(),"tame":set()}
    for i in range(40):
        S.call("rimworld/step_game_ticks", ticks=8)
        w,t=cur(wild),cur(tame)
        if w or t: print("   tick",S.ticks(),"wild",w,"tame",t, json.dumps(S.call("jawa/pawn_mental", pawn=(wild if w else tame), action="list", limit=1),default=str)[:300]); seen["wild"].add(w); seen["tame"].add(t)
    for c in calves:
        r=S.call("jawa/static_call", type=P, method="ProofEnrage", args=c)
        print("  ", str(r.get("result")).replace("\n"," | ")[:400])
    p=(S.call("jawa/pawn_get", pawn=col).get("pawns") or [{}])[0]
    print(name,"SUMMARY wild",seen["wild"],"tame",seen["tame"],"colonist hediffs",[h.get("def") for h in p.get("hediffs") or []][-4:])
scene("S1_wildCalves", int(sys.argv[1]), int(sys.argv[2]), "none")
scene("S2_tameCalves", int(sys.argv[1])+40, int(sys.argv[2]), "player")
