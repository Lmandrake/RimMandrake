import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
x0,x1=40,64
lanes={"RM_Glasswalk":150,"Concrete":154,"RM_Duckboards":158}
print("duck", S.call("jawa/set_terrain_batch", ops="RM_Duckboards:%d,158,%d,1"%(x0-1,x1-x0+3)).get("message"))
r=S.call("jawa/spawn_pawn", kindDef="Colonist", x=x0, z=162, faction="player", count=1); pid=r["pawns"][0]["id"]
p=S.call("jawa/pawn_get", pawn=pid)["pawns"][0]; print("pawn", pid, [h.get("def") for h in p.get("hediffs") or []])
res={}
for rep in range(2):
  for t,z in lanes.items():
    S.call("jawa/order_pawn", pawnId=pid, x=x0, z=z, waitTicks=600)
    t0=S.call("jawa/pawn_get", pawn=pid)["ticksGame"]
    S.call("jawa/order_pawn", pawnId=pid, x=x1, z=z, waitTicks=1)
    stun=0
    for i in range(80):
        S.run(10)
        q=S.call("jawa/pawn_get", pawn=pid); pp=q["pawns"][0]
        if pp["position"]["x"]==x1 and pp["position"]["z"]==z: break
    res.setdefault(t,[]).append(q["ticksGame"]-t0)
print("TIMES", res)
c=sum(res["Concrete"])
print("RATIO glass/concrete %.3f  duck/concrete %.3f"%(sum(res["RM_Glasswalk"])/c, sum(res["RM_Duckboards"])/c))
