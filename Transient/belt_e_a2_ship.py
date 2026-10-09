import sys,json,time
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
call=S.call
mid=S.biome_map(114501,"RM_SeabedFloor_GreySea",layer="RM_SeabedLayer",surface_biome="RM_GreySea",parent="RM_SeabedSite")
print("mapId",mid, call("jawa/map_info",mapId=mid) if False else "")
X,Z=30,30
print(call("jawa/destroy_batch",rects=f"{X-1},{Z-1},14,14",categories="Plant,Item,Filth,Building"))
r=call("jawa/set_substructure_batch",action="set",rect=f"{X},{Z},10,10",doLeavings=False); print(str(r)[:300])
r=call("jawa/spawn_batch",ops=f"GravEngine:{X+4},{Z+4}"); print(str(r)[:400])
print(call("jawa/gravship_status"))
print(call("jawa/static_call",type="RimMandrake.TerminalBiomes.RM_GreyHullCrustProof",method="ProofState",args="0"))
