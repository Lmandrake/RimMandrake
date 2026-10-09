import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
tiles=[114505,114506,114507]
for idx in range(2,12):
    m=S.call("jawa/set_current_map",mapId=idx)
    if not S.ok(m): continue
    info=S.call("jawa/map_info"); t=info.get("tile"); print(idx,t,info.get("mapBiome"))
    if t in tiles:
        print(str(S.drop_map(idx,t,back=0))[:80])
S.call("jawa/set_current_map",mapId=0)
print(json.dumps(S.call("jawa/map_info"))[:100])
