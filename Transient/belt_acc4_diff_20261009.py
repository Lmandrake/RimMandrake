import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
T=114504
mid=S.biome_map(T,"RM_SeabedFloor_TheChill",layer="RM_SeabedLayer",surface_biome="RM_TheChill",parent="RM_SeabedSite")
PID=[None]
def cmin(pid): return S.call("jawa/pawn_stats",pawn=pid,stats="ComfyTemperatureMin")["stats"][0]["value"]
def hold(sc,temp,n):
    t0=S.ticks()
    while S.ticks()-t0<n: sc.heat(6,2,temp); S.call('jawa/pawn_health',pawn=PID[0],action='heal'); S.run(60)
    return S.ticks()-t0
def deplete(sc,p):
    t0=S.ticks()
    while cmin(p)<-139 and S.ticks()-t0<20000: hold(sc,-15,500)
    return S.ticks()-t0
def partial(sc,p):
    sc.put("RM_HeatedSuitCharger",4,2); c=sc.find("RM_HeatedSuitCharger"); S.call("jawa/power_net",thing=c["id"],forcePowerOn=True)
    n=0
    while cmin(p)>-139 and n<2000: hold(sc,21,60); n+=60
    S.call("jawa/destroy_batch",ids=c["id"]) if False else print('  charger power',S.call('jawa/comp_read',thing=c['id'],comp='PowerTrader',members='PowerOn').get('values'),'pawn',S.call('jawa/pawn_get',pawn=PID[0])['pawns'][0]['position']); S.call("jawa/damage",damageDef="Bullet",amount=99999,thingId=c["id"],allowColonists=True)
    S.call("jawa/clear_area",rect=S.rect(24,22,1,1),dryRun=False)
    return n
try:
    for arm,temp in (("WARM",21),):
        with S.Scene("suit",20,20,9,8) as sc:
            sc.room(); p=sc.colonist(6,2); PID[0]=p; S.call("jawa/pawn_gear",pawn=p,action="wear",**{"def":"RM_ChillHeatedSuit"})
            d=deplete(sc,p); print(arm,"alive?",str(S.call("jawa/pawn_get",pawn=p))[:0] or "",end=""); print(arm,"depleted after",d,cmin(p))
            n=partial(sc,p); print(arm,"recharged-just-above-zero after",n,"ticks ->",cmin(p),"charger left:",sc.find("RM_HeatedSuitCharger").get("id"))
            g=S.call("jawa/pawn_get",pawn=p)["pawns"][0]; print("  pawn pos",g["position"],[h["def"] for h in g["hediffs"]],"chg",sc.find("RM_HeatedSuitCharger"))
            n=hold(sc,temp,2500); print(arm,"after",n,"ticks at",temp,"->",cmin(p),"temp",sc.temp(6,2))
except Exception:
    import traceback; traceback.print_exc()
finally:
    S.drop_map(mid,T,back=0)
