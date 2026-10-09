import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
P=lambda r:{k:r.get(k) for k in ("success","message","participants","started","error","stack")}
ideo=None
mid=S.biome_map(114505,"Desert",size=75)
try:
    d=S.call("jawa/get_defs",defs="PreceptDef/RUT_Ritual_NineFaults"); print("defs",d.get("success"),d.get("foundCount"),d.get("notFound"))
    io=S.call("jawa/ideo_of",limit=5); print(json.dumps(io)[:300])
    nm=[i.get("name") for i in (io.get("ideos") or [])][:1] or [None]
    ideoname=S.call("jawa/faction_ideo_get",factionDefName="PlayerColony")
    print(json.dumps(ideoname)[:300])
    sc=S.Scene("nine",30,30,9,9); sc.__enter__()
    sc.put("ElectricSmelter",4,4)
    m=sc.find("ElectricSmelter"); print("machine",m.get("id"))
    cols=[sc.colonist(1,1),sc.colonist(2,1),sc.colonist(3,1)]
    r=S.call("rimworld/apply_architect_designator",designatorId="architect-designator:orders:highlight-designator-tutortagnotset-7",x=m["x"],z=m["z"]); print("claim",str(r)[:300])
    open("/dev/null")
finally:
    pass
print("mid",mid)
