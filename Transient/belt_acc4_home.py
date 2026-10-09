import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
T=114504
mid=S.biome_map(T,"RM_SeabedFloor_TheChill",layer="RM_SeabedLayer",surface_biome="RM_TheChill",parent="RM_SeabedSite")
try:
    mi=S.call("jawa/map_info"); print("current",mi.get("mapId"),mi.get("mapBiome"),"layer",mi.get("layer"))
    print("homes",[(m.get("mapId"),m.get("biome"),m.get("isPlayerHome")) for m in (S.call("jawa/map_info",all=True).get("maps") or [])][:6] if False else "")
    r=S.call("jawa/static_call",type="RimMandrake.EnvironmentalHazards.RM_SurfaceHome",method="get_AnyPlayerSurfaceHomeMap",args="[]"); print(json.dumps(r)[:500])
except Exception:
    import traceback; traceback.print_exc()
finally:
    S.drop_map(mid,T,back=0)
