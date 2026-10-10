import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
K="RSW_ShrublandGiant"
def sp(kind,x,z,fac,n=1):
    r=S.call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=fac, count=n); return [p.get("id") for p in (r.get("pawns") or [])]
def cur(pid): return S.call("jawa/pawn_mental", pawn=pid, action="list", limit=1).get("currentState")
def scene(name,X,Z,calfFac):
    calves=sp(K,X,Z,calfFac,3)
    ages=[S.call("jawa/set_pawn_age", pawn=c, biologicalYears=0.05, chronologicalYears=0.05, allowBackwards=True).get("success") for c in calves]
    wild=sp(K,X+7,Z,"none")[0]; tame=sp(K,X-7,Z,"player")[0]
    col=sp("Colonist",X+1,Z,"player")[0]; S.call("jawa/set_draft", pawnId=col)
    print(name,"ages set",ages,"calves",calves)
    seen={}
    for i in range(10):
        S.run(125)
        w,t,c=cur(wild),cur(tame),[cur(x) for x in calves]
        seen.setdefault("wild",set()).add(w); seen.setdefault("tame",set()).add(t)
        print(name,"t+%d"%((i+1)*125),"wild",w,"tame",t,"calves",c)
    p=(S.call("jawa/pawn_get", pawn=col).get("pawns") or [{}])[0]
    print(name,"SUMMARY wild",seen["wild"],"tame",seen["tame"],"colonist hediffs",[h.get("def") for h in p.get("hediffs") or []])
scene("S1_wildCalves",120,140,"none")
scene("S2_tameCalves",150,140,"player")
