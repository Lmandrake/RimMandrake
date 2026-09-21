import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
DOORS=[(140,130),(147,132),(155,128),(196,103)]
with RimBridge(host, port, token) as rb:
    r=rb.call("jawa/destroy_batch",{"rects":";".join("%d,%d,1,1"%(x,z) for x,z in DOORS),"categories":"Building"})
    print("destroy:", json.dumps({k:v for k,v in r.items() if k!="operation"})[:250])
    r=rb.call("jawa/spawn_batch",{"ops":";".join("Wall:%d,%d"%(x,z) for x,z in DOORS),"stuff":"Steel"})
    print("walls:", json.dumps({k:v for k,v in r.items() if k!="operation"})[:250])
    for x,z in DOORS:
        ci=rb.call("rimworld/get_cell_info",{"x":x,"z":z})["cell"]
        print((x,z),"solid",ci.get("solidThingDefs"),"walkable",ci.get("walkable"))
    for n,(x,z) in {"PEN_BARE":(138,130),"PEN_HELM":(146,130),"PEN_SYM":(154,130),"R6":(193,103)}.items():
        rg=rb.call("jawa/room_get",{"x":x,"z":z,"includeOutdoors":True}); rm=(rg.get("rooms") or [{}])[0]
        print(n,"cells",rm.get("cellCount"),"outdoorTemp?",rm.get("usesOutdoorTemperature"),"openRoof",rm.get("openRoofCount"))
