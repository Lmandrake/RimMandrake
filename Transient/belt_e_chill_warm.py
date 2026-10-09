import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
call=S.call
S.drop_map(1,114501)
T=114504
mid=S.biome_map(T,"RM_SeabedFloor_TheChill",layer="RM_SeabedLayer",surface_biome="RM_TheChill",parent="RM_SeabedSite")
print("map",mid,flush=True)
def where(pid):
    for t in call("jawa/pawn_get",pawn="").get("pawns",[]):
        if t["thingId"]==pid: return (t["x"],t["z"])
def cmin(pid): return call("jawa/pawn_stats",pawn=pid,stats="ComfyTemperatureMin")["stats"][0]["value"]
try:
    with S.Scene("suitw",20,20,9,8) as sc:
        sc.room(); sc.grid()
        x,z=sc.abs(5,5)
        ops=";".join("Heater:%d,%d"%sc.abs(5,k) for k in (1,2,3,4,5))
        print("heaters",call("jawa/build_batch",ops=ops,faction="PlayerColony").get("message"))
        call("jawa/map_commit",power=True,regions=True)
        p=sc.colonist(7,2); call("jawa/set_draft",pawnId=p,drafted=True); call("jawa/pawn_gear",pawn=p,action="wear",**{"def":"RM_ChillHeatedSuit"})
        q=sc.colonist(3,5); sc.fuel(q,n=75,ticks=1500)
        print("net",sc.netsize("Heater"))
        g=call("jawa/pawn_get",pawn=p)["pawns"][0]; print("PID",p,sc.abs(7,2),g.get("position"),[k for k in g.keys()][:40], "room?",call("jawa/room_heat",mode="get",x=sc.abs(7,2)[0],z=sc.abs(7,2)[1])); t0=S.ticks(); c0=cmin(p); print("start cmin",c0,"temp",sc.temp(7,2))
        for i in range(64):
            S.run(500); call("jawa/set_draft",pawnId=p,drafted=True); [call("jawa/pawn_need",pawn=p,action="need",need=n,level=1.0) for n in ("Food","Rest","Mood")]; call("jawa/pawn_health",pawn=p,action="heal"); call("jawa/pawn_health",pawn=q,action="heal")
            print(i,"ticks",S.ticks()-t0,"temp",sc.temp(7,2),"cmin",cmin(p),"pos",call("jawa/pawn_get",pawn=p)["pawns"][0]["position"],"inroom",(lambda g:21<=g["x"]<=27 and 21<=g["z"]<=26)(call("jawa/pawn_get",pawn=p)["pawns"][0]["position"]),flush=True)
except Exception:
    import traceback; traceback.print_exc()
finally:
    S.drop_map(mid,T,back=0)
