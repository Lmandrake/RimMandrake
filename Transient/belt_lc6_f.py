import sys; sys.path.insert(0,"Transient")
from belt_lc6_lib import *
call("jawa/set_terrain_batch", ops="Soil:195,20,40,10"); call("jawa/destroy_batch", rects="195,20,40,10", categories="All")
call("jawa/build_batch", ops="RM_AerialMast:200,25;RM_AerialMast:212,25;Battery:199,25,0", faction="player", wipeExisting=True); call("jawa/map_commit"); step(10)
for t in call("jawa/list_things", defName="Battery")["things"]:
    if t["z"]==25: call("jawa/battery_set", thing=t["id"], mode="setPct", value=1.0)
step(20); c=ap("census"); a=sorted([x for x in c["anchors"] if x["z"]==25], key=lambda x:x["x"]); print([(x["id"],x["x"],x["netLive"]) for x in a])
ap("kill:%d"%a[1]["id"]); step(30); ap("poll"); step(30)
c=ap("census"); a=[x for x in c["anchors"] if x["z"]==25]; print([(x["id"],x["netLive"],x["fallenLive"],len(x["fallen"])) for x in a]); print(json.dumps(a[0]["fallen"])[:300])
print(call("jawa/spawn_batch", ops="Filth_Fuel:212,25,1;Filth_Fuel:211,25,1;Filth_Fuel:210,25,1").get("thingsPlaced"))
for i in range(8):
    step(75); f=call("jawa/list_things", defName="Fire").get("countMatched"); print(i, "fires", f)
    if f: break
