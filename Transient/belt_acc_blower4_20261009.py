import sys,json,re
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
ST="RimMandrake.EnvironmentalHazards.RM_EnvironmentalHazardsSettings"
out={}
def get(f): return S.call("jawa/mod_settings_field",typeName=ST,action="get",field=f).get("value")
def setf(f,v): return S.call("jawa/mod_settings_field",typeName=ST,action="set",field=f,value=str(v))
orig={f:get(f) for f in ("dryAirBlowerPowerWatts","dryAirBlowerCoolingStrength","dryAirBlowerCoolingEnabled")}
out["orig"]=orig
def run1(label,watts,strength):
    setf("dryAirBlowerPowerWatts",watts); setf("dryAirBlowerCoolingStrength",strength)
    with S.Scene("b4"+label,80,200,12,8) as sc:
        sc.room()
        sc.put("RM_DryAirBlower",6,0,rot=2)
        sc.put("WoodFiredGenerator",5,1); sc.put("PowerConduit",6,1)
        S.call("jawa/map_commit",power=True,regions=True)
        pid=sc.colonist(8,3); sc.fuel(pid,n=40,ticks=900)
        b=sc.find("RM_DryAirBlower"); sc.put("Chemfuel",8,5,n=50)
        f=sc.find("Chemfuel")
        if label!="ctl": sc.order(pid,"Refuel",a=b["id"],b=f["id"],count=50)
        S.run(900)
        sc.heat(4,4,50)
        T=lambda:(S.call("jawa/room_get",x=sc.x+4,z=sc.z+4,includeOutdoors=True).get("rooms") or [{}])[0].get("temperature")
        t0=T(); ser=[t0]
        for i in range(8):
            S.run(250); ser.append(T())
        t1=ser[4]
        ins=sc.inspect(b["id"]); m=re.search(r"Power needed: [^\"]*",ins)
        t1=T()
        pn=S.call("jawa/power_net",thing=b["id"]).get("net",{}).get("currentEnergyGainRate")
        t2=ser[8]
        out[label]=dict(t0=t0,t500=t1,t2000=t2,ser=[round(v,2) for v in ser],power=m.group(0) if m else ins[:300],gain=pn)
try:
    run1("ctl",250,14)
    run1("s14",250,14)
    run1("s28",250,28)
    run1("s14b",250,14)
finally:
    for f,v in orig.items(): setf(f,v)
    out["restored"]={f:get(f) for f in orig}
print(json.dumps(out,default=str))
