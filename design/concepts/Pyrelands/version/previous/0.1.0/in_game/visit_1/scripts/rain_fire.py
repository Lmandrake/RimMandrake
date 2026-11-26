"""Fires under black rain vs clear: each sky fully transitioned (4500 ticks), each on its own fresh grassed, firebreak-ringed pad."""
import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,tk = resolve_endpoint()
S="RimMandrake.Pyrelands.RM_PyrelandsSettings"; ASH="RimMandrake.Pyrelands.PyrelandsAsh"
OFF=["burnLineEnabled","fireHawkSpreadEnabled","fireClockEnabled","burrowOnFireEnabled","furnaceThermalEnabled"]
W="0,0,250,250"; out={}
with RimBridge(h,p,tk) as rb:
    prior={f: rb.call("jawa/mod_settings_field",{"typeName":S,"action":"get","field":f}).get("value") for f in OFF}
    for f in OFF: rb.call("jawa/mod_settings_field",{"typeName":S,"action":"set","field":f,"value":"False"})
    def adv(n):
        left=n
        while left>0:
            s=min(2500,left); rb.call("jawa/safe_advance",{"ticks":s,"timeException":False}); left-=s
    def fires(rect): return rb.call("jawa/list_things",{"defName":"Fire","limit":1,"rect":rect}).get("countMatched")
    def wx(): r=rb.call("jawa/map_info",{}); return {k:r.get(k) for k in ("weather","curWeather","rainRate") if k in r}
    try:
        for w,(x,z) in (("RM_FE_BlackRain",(170,40)),("Clear",(200,40))):
            rect="%d,%d,8,8"%(x,z)
            ring=[(x-4,z-4,16,4),(x-4,z+8,16,4),(x-4,z,4,8),(x+8,z,4,8)]
            rb.call("jawa/set_terrain_batch",{"ops":";".join("Concrete:%d,%d,%d,%d"%r for r in ring),"layer":"top"})
            rb.call("jawa/set_plants",{"ops":";".join("CLEAR:%d,%d,%d,%d"%r for r in ring)})
            rb.call("jawa/set_terrain",{"x":x,"z":z,"terrainDef":"RM_FE_Ash_Deep","width":8,"height":8,"layer":"top"})
            pl=rb.call("jawa/set_plants",{"ops":"RM_FE_Plant_EmberGrass:"+rect,"growth":1.0})
            rb.call("jawa/map_fire",{"action":"extinguish","rect":W})
            rb.call("jawa/weather_set",{"weather":w,"lockWeather":True}); adv(4500)
            info=wx()
            r=rb.call("jawa/map_fire",{"action":"start","rect":rect,"fireSize":1.2})
            ser=[fires(rect)]
            for i in range(8): adv(250); ser.append(fires(rect))
            out[w]={"planted":pl.get("planted"),"started":r.get("firesStarted"),"fires_every_250":ser,"map_info":info}
            print(w, out[w])
    finally:
        rb.call("jawa/map_fire",{"action":"extinguish","rect":W})
        rb.call("jawa/weather_set",{"weather":"Clear","lockWeather":True}); adv(60); rb.call("jawa/weather_set",{"unlock":True})
        for f,v in prior.items(): rb.call("jawa/mod_settings_field",{"typeName":S,"action":"set","field":f,"value":str(v)})
# RIMMANDRAKE_TUNE_BLACK_RAIN_DOUSING_VANILLA_RAIN_TOO_WEAK: the black-rain pad reaches 0 fires >= 1,000 ticks before the Clear pad.
def out_at(w):
    ser=(out.get(w) or {}).get("fires_every_250") or []
    return next((i*250 for i,n in enumerate(ser) if n==0), None)
b,c=out_at("RM_FE_BlackRain"),out_at("Clear")
if c is None: c=len((out.get("Clear") or {}).get("fires_every_250") or [])*250   # still burning at the last sample: out no sooner than the next
out["verdict"]=("PASS" if b is not None and c-b>=1000 else "FAIL")+" black rain out at %s, clear at %s ticks"%(b,c)
print(out["verdict"])
json.dump(out, open(r"Transient\pv1\rain_fire.json","w"), indent=1)
