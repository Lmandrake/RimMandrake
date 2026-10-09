import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
mid=S.biome_map(114506,"RM_Stillsand",size=75)
print("biome",S.call("jawa/map_info").get("mapBiome"),"mid",mid)
d=S.call("jawa/get_defs",defs="PreceptDef/RUT_Ritual_TheReturn"); print("defs",d.get("success"),d.get("foundCount"))
print(json.dumps(S.call("jawa/ideo_precept_edit",ideo="Absolute Cave",action="add",precept="RUT_Ritual_TheReturn"))[:200])
sc=S.Scene("ret",30,30,9,9); sc.__enter__()
sc.put("RUT_DebtStone",4,4)
st=sc.find("RUT_DebtStone"); print("stone",st)
print(json.dumps(S.call("jawa/set_thing_props",thing=st["id"],faction="PlayerColony"))[:200])
sc.put("RM_StilledWater",5,5,n=10)
cols=[sc.colonist(1,1),sc.colonist(2,1),sc.colonist(3,1)]
r=S.call("jawa/ritual_start",ritual="RUT_Ritual_TheReturn",targetThingId=st["id"],organizer=cols[0]); print(json.dumps(r)[:600])
S.run(3300)
print("water left",json.dumps(S.call("jawa/list_things",defName="RM_StilledWater",rect=sc.rect).get("perDef")))
print(json.dumps(S.call("jawa/drain_log",contains="Exception",limit=3))[:400])
print(json.dumps(S.call("jawa/drain_log",contains="Return",limit=5))[:700])
