import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
T=114504
mid=S.biome_map(T,"RM_SeabedFloor_TheChill",layer="RM_SeabedLayer",surface_biome="RM_TheChill",parent="RM_SeabedSite")
def cmin(pid): return S.call("jawa/pawn_stats",pawn=pid,stats="ComfyTemperatureMin")["stats"][0]["value"]
try:
    with S.Scene("suit",20,20,9,8) as sc:
        sc.room()
        p=sc.colonist(6,2); S.call("jawa/pawn_gear",pawn=p,action="wear",**{"def":"RM_ChillHeatedSuit"})
        mn=99; t0=S.ticks(); last=cmin(p); print("t0",t0,last)
        for i in range(480):
            sc.heat(6,2,-15); S.run(250); t=sc.temp(6,2); mn=min(mn,t); c=cmin(p)
            if c!=last: print("CHANGE",c,"after ticks",S.ticks()-t0,"temp",t,"min",mn); last=c
            if S.ticks()-t0>30000: break
        print("end",S.ticks()-t0,mn)
except Exception:
    import traceback; traceback.print_exc()
finally:
    S.drop_map(mid,T,back=0)
