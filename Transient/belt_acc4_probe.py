import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
T=114504
mid=S.biome_map(T,"RM_SeabedFloor_TheChill",layer="RM_SeabedLayer",surface_biome="RM_TheChill",parent="RM_SeabedSite")
try:
    with S.Scene("suit",20,20,12,8) as sc:
        sc.room(); p=sc.colonist(2,2)
        w=S.call("jawa/pawn_gear",pawn=p,action="wear",**{"def":"RM_ChillHeatedSuit"})
        
        r=S.call('jawa/thing_stats',pawn=p,slot='apparel',limit=3); print(json.dumps(r)[:900])
        print(S.call('jawa/comp_read',thing='RM_ChillHeatedSuit',comp='HeatedSuitBattery',members=''))
finally:
    S.drop_map(mid,T,back=0)
