import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
PENS={"BARE":(136,128),"HELM":(144,128),"SYM":(152,128)}
with RimBridge(host, port, token) as rb:
    for g,(x,z) in PENS.items():
        r=rb.call("jawa/make_empty_room",{"rect":"%d,%d,5,5"%(x,z),"wallDef":"Wall","stuffDef":"Steel","doorDef":"Door","floorDef":"Concrete","roofDef":"RoofConstructed"})
        d=r.get("doorAt")
        rr=rb.call("jawa/set_roof_batch",{"ops":"None:%d,%d,5,5"%(x,z)})
        print(g,"room",r.get("success"),"door",d,"unroof",rr.get("success"),json.dumps({k:v for k,v in rr.items() if k not in("operation",)})[:160])
        ci=rb.call("rimworld/get_cell_info",{"x":x+2,"z":z+2})["cell"]
        print("   center terrain",ci.get("terrainDefName"),"roof",ci.get("roofDefName"))
