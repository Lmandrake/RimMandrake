import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
def j(x,n=300): return json.dumps(x,default=str)[:n]
x0,x1=40,64
lanes={"RM_Glasswalk":150,"Concrete":154,"RUT_Duckboards":158}
for t,z in lanes.items():
    S.call("jawa/clear_area", rect="%d,%d,%d,3"%(x0-2,z-1,x1-x0+5)) 
    print("terrain",t,j(S.call("jawa/set_terrain_batch", ops="%s:%d,%d,%d,1"%(t,x0-1,z,x1-x0+3)),150))
res={}
for t,z in lanes.items():
    r=S.call("jawa/spawn_pawn", kindDef="Colonist", x=x0, z=z, faction="player", count=1); pid=r["pawns"][0]["id"]
    S.call("jawa/order_pawn", pawnId=pid, x=x0, z=z, waitTicks=30)
    t0=S.call("jawa/pawn_get", pawn=pid)["ticksGame"]
    S.call("jawa/order_pawn", pawnId=pid, x=x1, z=z, waitTicks=1)
    hist=[]
    for i in range(80):
        S.run(10)
        p=S.call("jawa/pawn_get", pawn=pid); pp=p["pawns"][0]; pos=pp["position"]
        hist.append(pos["x"])
        if pos["x"]==x1 and pos["z"]==z: break
    dt=p["ticksGame"]-t0
    res[t]=dt; print("LANE",t,"ticks",dt,"cells",x1-x0,"offlane", any(False for _ in []), "hediffs",[h.get("def") for h in pp.get("hediffs") or []][-4:])
print("RATIO glass/concrete %.3f  duck/concrete %.3f (glass expect ~ (base+3)/base)"%(res["RM_Glasswalk"]/res["Concrete"], res["RUT_Duckboards"]/res["Concrete"]))
print("DEFS", j(S.call("jawa/get_defs", defs="TerrainDef/RM_Glasswalk;TerrainDef/RUT_Duckboards;TerrainDef/Concrete", fields="pathCost,generatedFilth,filthAcceptanceMask"),900))
