import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
SITE=[("RUT_AgelessCap",100,135),("RUT_RegenerantVeil",110,135),("RUT_FalseFruit",120,135)]
with RimBridge(host, port, token) as rb:
    print([ (x["requested"],x["found"]) for x in rb.call("jawa/get_defs",{"defs":"JobDef/Harvest;JobDef/HarvestDesignated;JobDef/CutPlant","fields":"defName"}).get("defs",[])])
    rb.call("jawa/destroy_batch",{"rects":"95,130,32,12","categories":"All"})
    rb.call("jawa/set_terrain_batch",{"ops":"Soil:95,130,32,12"})
    ch=rb.call("rimworld/list_debug_action_children", {"path":"Actions"})["children"]
    P=next(c["path"] for c in ch if c["path"].endswith("T: Grow plant to maturity"))
    for d,x,z in SITE:
        rb.call("jawa/spawn_batch",{"ops":"%s:%d,%d,1"%(d,x,z)})
        rb.call("rimworld/execute_debug_action",{"path":P,"x":x,"z":z})
        t=rb.call("jawa/list_things",{"defName":d})
        print(d, [(q["id"],q["x"],q["z"]) for q in t.get("things",[])], rb.call("jawa/inspect_string",{"defName":d}).get("things",[{}])[0].get("inspect"))
