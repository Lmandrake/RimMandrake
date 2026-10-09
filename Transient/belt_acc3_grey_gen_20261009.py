import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
S.drop_map(1,114500)
mid=S.biome_map(114501,"RM_SeabedFloor_GreySea",layer="RM_SeabedLayer",surface_biome="RM_GreySea",parent="RM_SeabedSite")
print("mapId",mid)
r=S.call("jawa/list_things",limit=1,includePawns=False)
print(r.get("scanned"),json.dumps(r.get("perDef"))[:900])
