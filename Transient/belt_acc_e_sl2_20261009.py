import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
out={}
with S.Scene("slp4",40,40,30,12) as sc:
    sc.put("RM_SleeperVenomvine",2,2)
    r=S.call("jawa/spawn_pawn",kindDef="Hare",x=sc.x+3,z=sc.z+2,faction="player",count=1); out["spawn"]=str(r)[:300]
    for i in range(4):
        th=sc.things().get("things") or []
        out["t%d"%i]=[(t["def"],t["x"]-sc.x,t["z"]-sc.z) for t in th if t["def"] in("Hare","RM_SleeperVenomvine","RM_SleeperVenomvineAwake")]
        S.run(15)
print(json.dumps(out,default=str))
