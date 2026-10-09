import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
T=114504
mid=S.biome_map(T,"RM_SeabedFloor_TheChill",layer="RM_SeabedLayer",surface_biome="RM_TheChill",parent="RM_SeabedSite")
def ins(pid):
    r=S.call("jawa/pawn_stats",pawn=pid,stats="ComfyTemperatureMin")
    return [x["value"] for x in r["stats"]]
def dress(pid): S.call("jawa/pawn_gear",pawn=pid,action="wear",**{"def":"RM_ChillHeatedSuit"})
def hold(sc,temp,n,every=200):
    for i in range(0,n,every): sc.heat(6,2,temp); S.run(every)
try:
    with S.Scene("suit",20,20,9,8) as sc:
        sc.room()
        p1=sc.colonist(6,2); dress(p1); print("full",ins(p1))
        # B: warm roofed control for 16000 ticks
        hold(sc,21,16000); print("T2 warm roofed 16000t:",ins(p1),"temp",sc.temp(6,2))
        hold(sc,-15,16000,400); print("T1 cold roofed 16000t:",ins(p1),"temp",sc.temp(6,2))
        # depleted. Charger behind wall (adjacent room B, x 32..) within 3.9
        with S.Scene("suitB",28,20,8,8) as sb:
            sb.room(); 
            sb.put("RM_HeatedSuitCharger",1,2); ch=sb.find("RM_HeatedSuitCharger"); print("chargerB",ch.get("id"),ch.get("x"),ch.get("z"))
            S.call("jawa/power_net",thing=ch["id"],forcePowerOn=True)
            hold(sc,21,1000); print("T3 warm, charger behind wall (dist~",abs(ch['x']-sc.abs(6,2)[0]),") 1000t:",ins(p1))
            sc.put("RM_HeatedSuitCharger",4,2); c2=sc.find("RM_HeatedSuitCharger"); print("chargerA",c2.get("id"),c2.get("x"),c2.get("z"))
            S.call("jawa/power_net",thing=c2["id"],forcePowerOn=True)
            hold(sc,21,1000); print("T4 warm, same-room powered charger 1000t:",ins(p1))
except Exception as e:
    import traceback; traceback.print_exc()
finally:
    S.drop_map(mid,T,back=0)
