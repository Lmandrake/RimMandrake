import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
out={}
with S.Scene("slp5",40,40,6,5) as sc:
    sc.room(roof=False)
    sc.floor("Soil",(1,1,4,3))
    sc.put("RM_SleeperVenomvine",2,2)
    r=S.call("jawa/spawn_pawn",kindDef="Hare",x=sc.x+3,z=sc.z+2,faction="player",count=1)
    for i in range(4):
        th=sc.things().get("things") or []
        out["t%d"%i]=[(t["def"],t["x"]-sc.x,t["z"]-sc.z) for t in th if t["def"] not in ("Wall","BlocksGranite") and "Wall" not in t["def"]]
        S.run(60)
print(json.dumps(out,default=str))
