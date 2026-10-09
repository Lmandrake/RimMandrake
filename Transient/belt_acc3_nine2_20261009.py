import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
print(json.dumps(S.call("jawa/ideo_precept_edit",ideo="Absolute Cave",action="add",precept="RUT_Ritual_NineFaults"))[:300])
sc=S.Scene("nine",30,30,9,9)
m=sc.find("ElectricSmelter"); cols=[p for p in S.call("jawa/list_pawns",rect=sc.rect,limit=20).get("pawns",[])]
print(len(cols),[c.get("id") for c in cols])
r=S.call("jawa/ritual_start",ritual="RUT_Ritual_NineFaults",targetThingId=m["id"],organizer=cols[0]["id"])
print(json.dumps(r)[:1500])
S.run(300)
print(json.dumps(S.call("jawa/drain_log",contains="Exception",limit=5))[:500])
