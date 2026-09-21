import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
DOORS=[(140,130),(147,132),(155,128),(196,103)]
with RimBridge(host, port, token) as rb:
    ids=[]
    for x,z in DOORS:
        t=rb.call("jawa/list_things",{"defName":"Door","rect":"%d,%d,1,1"%(x,z)})
        ids += [th["id"] for th in t.get("things",[])]
    print("doors found:", ids)
    r=rb.call("jawa/destroy_batch",{"thingIds":",".join(ids)})
    print("destroy:", json.dumps({k:v for k,v in r.items() if k!="operation"})[:300])
    ops=";".join("Wall:%d,%d"%(x,z) for x,z in DOORS)
    r=rb.call("jawa/spawn_batch",{"ops":ops,"stuff":"Steel"})
    print("walls:", json.dumps({k:v for k,v in r.items() if k!="operation"})[:300])
    for x,z in DOORS:
        ci=rb.call("rimworld/get_cell_info",{"x":x,"z":z})["cell"]
        print((x,z),"solid",ci.get("solidThingDefs"),"walkable",ci.get("walkable"))
