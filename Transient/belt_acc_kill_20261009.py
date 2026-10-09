import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
out={}
with S.Scene("kill",80,200,12,8) as sc:
    sc.room()
    col=sc.colonist(2,2)
    out["host"]=[]
    for i in range(3):
        try:
            r=S.call("jawa/spawn_pawn",kindDef="Pirate",x=sc.x+5+i,z=sc.z+4,faction="hostile",count=1); out["host"].append(str(r)[:200])
        except Exception as e: out["host"].append("ERR "+str(e)[:100])
    try:
        r=S.call("jawa/spawn_pawn",kindDef="Muffalo",x=sc.x+8,z=sc.z+5,faction="player",count=1); out["tame"]=str(r)[:200]
    except Exception as e: out["tame"]="ERR "+str(e)[:100]
    S.run(30)
    lp=S.call("jawa/list_pawns"); out["before"]=str(lp)[:600]
    k=S.call("jawa/kill_hostiles"); out["kill"]=json.dumps({a:k[a] for a in k if a not in("operation","state")},default=str)[:600]
    out["after"]=str(S.call("jawa/list_pawns"))[:600]
    out["col_alive"]=str(S.pawn_state(col))[:200] if hasattr(S,"pawn_state") else ""
d=S.call("jawa/get_defs",defs="DesignationCategoryDef/Structure",fields="specialDesignatorClasses")
out["defs"]=str(d)[:500]
print(json.dumps(out,default=str))
