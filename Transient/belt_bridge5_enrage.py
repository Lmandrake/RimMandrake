import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
def j(x,n=300): return json.dumps(x,default=str)[:n]
K="RSW_ShrublandGiant"
def sp(kind,x,z,fac,n=1):
    r=S.call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=fac, count=n)
    ids=[p.get("id") for p in (r.get("pawns") or [])]
    if not ids: print("SPAWNFAIL",kind,j(r))
    return ids
def ms(pid):
    p=(S.call("jawa/pawn_get", pawn=pid).get("pawns") or [{}])[0]
    m=S.call("jawa/pawn_mental", pawn=pid, action="list")
    return j({k:m.get(k) for k in m if k in ("mentalState","state","current","inMentalState","states","pawns")},220)
def scene(name,X,Z,calfFac):
    calves=sp(K,X,Z,calfFac,3)
    for c in calves: S.call("jawa/set_pawn_age", pawn=c, biologicalYears=0.05, chronologicalYears=0.05, allowBackwards=True)
    wild=sp(K,X+9,Z,"none")[0]; tame=sp(K,X-9,Z,"player")[0]
    col=sp("Colonist",X+1,Z+1,"player")[0]; S.call("jawa/set_draft", pawnId=col, drafted=True) if False else S.call("jawa/set_draft", pawnId=col)
    S.run(600)
    print(name,"calves",calves,"wildAdult",wild,ms(wild)); print(name,"tameAdult",tame,ms(tame))
scene("S1_wildCalves",120,95,"none")
scene("S2_tameCalves",120,120,"player")
