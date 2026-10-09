import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
T=114504
mid=S.biome_map(T,"RM_SeabedFloor_TheChill",layer="RM_SeabedLayer",surface_biome="RM_TheChill",parent="RM_SeabedSite")
try:
    with S.Scene("suit",20,20,9,8) as sc:
        sc.room(); p=sc.colonist(6,2)
        for i in range(4):
            sc.heat(6,2,21); S.run(100)
            a=S.call("jawa/thing_ambient_temp",thing=p)
            print(i,"cell_temp",sc.temp(6,2),"pawn ambient",a.get("ambientTemperature",a.get("temperature",str(a)[:200])))
        g=S.call("jawa/pawn_get",pawn=p)["pawns"][0]["position"]; print("pos",g, "room_heat read", str(S.call("jawa/room_heat",mode="get",x=g["x"],z=g["z"]))[:200])
except Exception:
    import traceback; traceback.print_exc()
finally:
    S.drop_map(mid,T,back=0)
