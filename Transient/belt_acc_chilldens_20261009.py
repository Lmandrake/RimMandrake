import sys,json,collections
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
out={}
for i,tile in enumerate((114490,114491)):
    mid=S.biome_map(tile,"RM_TheChill",layer="RM_SeabedLayer",surface_biome="RM_TheChill")
    try:
        S.run(30)
        r=S.call("jawa/list_pawns",mapId=mid) if True else {}
        ps=r.get("pawns") or []
        out["map%d"%i]=dict(mapId=mid,msg=r.get("message"),pawns=[(p.get("kindDef"),p.get("isPlayer"),p.get("hostile"),p.get("intelligence"),p.get("faction")) for p in ps])
    finally:
        S.drop_map(mid,tile)
print(json.dumps(out,default=str))
