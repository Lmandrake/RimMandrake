import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r=rb.call("jawa/make_empty_room",{"rect":"60,100,7,7","wallDef":"Wall","stuffDef":"Steel","doorDef":"Door","floorDef":"Concrete","roofDef":"RoofConstructed"})
    print("coldroom",r.get("success"),r.get("doorAt"))
    rb.call("jawa/spawn_batch",{"ops":"RUT_Tea_AgeReversal:63,103,1;RUT_Symbiont_Mycoid:63,104,1"})
    rb.call("jawa/spawn_batch",{"ops":"RUT_Tea_Bioregeneration:143,103,1"})   # warm control in R1
    print("cold items:", [(t["id"],t["def"]) for t in rb.call("jawa/list_things",{"rect":"61,101,5,5"}).get("things",[])])
    h=rb.call("jawa/room_heat",{"x":63,"z":103,"mode":"set","value":-15})
    print("set temp:", json.dumps({k:v for k,v in h.items() if k!="operation"})[:250])
    print("cellTemp:", rb.call("jawa/cell_temperature",{"cell":"63,103"}).get("temperature"))
    print("control cellTemp:", rb.call("jawa/cell_temperature",{"cell":"143,103"}).get("temperature"))
