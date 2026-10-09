import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
P=lambda m,a="x": str((S.call("jawa/static_call",type="RimMandrake.TerminalBiomes.RM_GreyHullCrustProof",method=m,args=a) or {}).get("result"))[:400]
mid=S.biome_map(114502,"RM_GreySea",layer="RM_SeabedLayer",surface_biome="RM_GreySea")
print("biome",S.call("jawa/map_info").get("mapBiome"))
sc=S.Scene("crustctl",40,60,11,11); sc.__enter__()
sc.room(roof=True,floor="Substructure"); sc.put("GravEngine",5,5); sc.put("Door",5,0,stuff="BlocksGranite")
S.call("jawa/map_commit",full=True)
print("adv",P("ProofAdvance","16"))
e=sc.find("GravEngine"); print(sc.inspect(e.get("id"))[:900])
print("tear",P("ProofTearFree"))
S.drop_map(mid,114502,back=2)
