import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for x,z in [(40,40)]:
        ci=rb.call("rimworld/get_cell_info",{"x":x,"z":z})["cell"]
        print((x,z), ci.get("terrainDefName"), ci.get("walkable"), ci.get("solidThingDefs"))
    rb.call("jawa/destroy_batch",{"rects":"35,35,12,12","categories":"All"})
    rb.call("jawa/set_terrain_batch",{"ops":"Soil:35,35,12,12"})
    print(rb.call("jawa/spawn_batch",{"ops":"RUT_PaleTree:40,40,1"}).get("message"))
    t=[x for x in rb.call("jawa/list_things",{"defName":"RUT_PaleTree"}).get("things",[])]
    print("trees:",[(x["id"],x["x"],x["z"]) for x in t])
    ch=rb.call("rimworld/list_debug_action_children", {"path":"Actions"})["children"]
    P=next(c["path"] for c in ch if c["path"].endswith("T: Grow plant to maturity"))
    print("grow:", rb.call("rimworld/execute_debug_action",{"path":P,"x":40,"z":40}).get("success"))
    print(rb.call("jawa/spawn_batch",{"ops":"MeditationSpot:43,40,1"}).get("message"))
