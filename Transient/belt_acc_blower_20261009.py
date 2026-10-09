import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
out={}
def run1(label,x,fuelblower=True):
    with S.Scene("blower_"+label,x,200,12,8) as sc:
        sc.room()
        sc.put("RM_DryAirBlower",6,0,rot=2)
        sc.put("WoodFiredGenerator",5,1); sc.put("PowerConduit",6,1)
        S.call("jawa/map_commit",power=True,regions=True)
        pid=sc.colonist(8,3)
        sc.fuel(pid,n=40,ticks=900)
        b=sc.find("RM_DryAirBlower")
        sc.put("Chemfuel",8,5,n=50)
        if fuelblower:
            f=sc.find("Chemfuel"); sc.order(pid,"Refuel",a=b["id"],b=f["id"],count=50); S.run(900)
        out[label+"_power"]=json.dumps(S.call("jawa/power_net",thing=b["id"]),default=str)[:400]
        out[label+"_inspect0"]=sc.inspect(b["id"])[:300]
        sc.heat(4,4,35)
        out[label+"_roomget"]=json.dumps(S.call("jawa/room_get",x=sc.x+4,z=sc.z+4),default=str)[:500]
        samples=[]
        for i in range(9):
            samples.append((((S.call("jawa/room_get",x=sc.x+4,z=sc.z+4,includeOutdoors=True).get("rooms") or [{}])[0].get("temperature")), sc.temp(6,-2)))
            S.run(250)
        out[label+"_samples"]=samples
        out[label+"_inspect"]=sc.inspect(b["id"])[:300]
        out[label+"_comp"]=S.call("jawa/comp_read",thing=b["id"],comp="BlowerRoomCooler",members="enabled").get("values")
run1("ctl",80,False)
run1("on",80,True)
print(json.dumps(out,default=str))
