import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
out={}
mid=S.biome_map(114480,"RM_Greentide")
try:
    mi=S.call("jawa/map_info"); out["map"]={k:mi.get(k) for k in("mapId","mapBiome","sizeX","sizeZ")}
    r=S.call("jawa/list_pawns",kindDef="RM_Illisk",limit=100)
    out["list_keys"]=list(r.keys()) if isinstance(r,dict) else str(r)[:200]
    ps=r.get("pawns") or []
    out["illisk_n"]=len(ps)
    out["sample"]=ps[:3]
    out["total_pawn_info"]={k:r.get(k) for k in r if k!="pawns"}
finally:
    pass
print(json.dumps(out,default=str)[:2500])
open("Transient/belt_acc2_illisk_map_id.txt","w").write(str(mid))
