import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
call=S.call
S.drop_map(2,114504) if False else None
T=114504
mid=S.biome_map(T,"RM_SeabedFloor_TheChill",layer="RM_SeabedLayer",surface_biome="RM_TheChill",parent="RM_SeabedSite")
print("map",mid,flush=True)
def cmin(pid):
    r=call("jawa/pawn_stats",pawn=pid,stats="ComfyTemperatureMin")
    return r["stats"][0]["value"] if "stats" in r else str(r)[:120]
def pos(pid): return call("jawa/pawn_get",pawn=pid)["pawns"][0]["position"]
def inroom(pid): g=pos(pid); return 21<=g["x"]<=27 and 21<=g["z"]<=26
try:
    with S.Scene("suitc",20,20,9,8) as sc:
        sc.room(); sc.grid()
        print("roomB",call("jawa/make_empty_room",rect="28,20,9,8",stuffDef="BlocksGranite",floorDef="TileGranite",roofDef="RoofConstructed").get("success"))
        ops=";".join("Heater:%d,%d"%sc.abs(5,k) for k in (1,2,3,4,5))
        print("heaters",call("jawa/build_batch",ops=ops,faction="PlayerColony").get("message"))
        call("jawa/build_batch",ops="RM_HeatedSuitCharger:29,22",faction="PlayerColony")
        call("jawa/map_commit",power=True,regions=True)
        p=sc.colonist(7,2); call("jawa/set_draft",pawnId=p,drafted=True); call("jawa/pawn_gear",pawn=p,action="wear",**{"def":"RM_ChillHeatedSuit"})
        q=sc.colonist(3,5)
        sc.fuel(q,n=75,ticks=1500); call("jawa/set_draft",pawnId=q,drafted=True)
        HT=[th["id"] for th in call("jawa/list_things",defName="Heater",limit=9)["things"]]
        def heaters(on):
            for h in HT: call("jawa/power_net",thing=h,forcePowerOn=on)
        heaters(False)
        ch=call("jawa/list_things",defName="RM_HeatedSuitCharger",limit=2)["things"][0]["id"]
        print("charger power",call("jawa/power_net",thing=ch,forcePowerOn=True).get("powerOnAfter"),"p",pos(p),"c",ch)
        HON=[False]
        def chunk(tag,n=500):
            S.run(n)
            call("jawa/set_draft",pawnId=p,drafted=True)
            for who in (p,q):
                for nd in ("Food","Rest","Mood"): call("jawa/pawn_need",pawn=who,action="need",need=nd,level=1.0)
                call("jawa/pawn_health",pawn=who,action="heal")
            call("jawa/power_net",thing=ch,forcePowerOn=True); heaters(HON[0])
            return cmin(p), sc.temp(7,2), inroom(p)
        # phase 1: deplete in the cold (generator unfuelled, no heat)
        t0=S.ticks()
        while True:
            c,t,ir=chunk("dep")
            if (S.ticks()-t0)%3000<500: print("dep",S.ticks()-t0,c,round(t),ir,flush=True)
            if c>-139 or S.ticks()-t0>24000: break
        print("DEPLETED at",S.ticks()-t0,c,ir,flush=True)
        # phase 2: warm room A, charger behind the wall in B
        HON[0]=True; heaters(True)
        for i in range(8):
            c,t,ir=chunk("warm",1000); print("warm_wallcharger",i,c,round(t),ir,flush=True)
        # phase 3: charger in the wearer's own room
        call("jawa/build_batch",ops="RM_HeatedSuitCharger:25,22",faction="PlayerColony")
        for th in call("jawa/list_things",defName="RM_HeatedSuitCharger",limit=5)["things"]: call("jawa/power_net",thing=th["id"],forcePowerOn=True)
        for i in range(8):
            c,t,ir=chunk("same"); print("same_room_charger",i,c,round(t),ir,flush=True)
except Exception:
    import traceback; traceback.print_exc()
finally:
    S.drop_map(mid,T,back=0)
