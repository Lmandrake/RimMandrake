import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
ROOMS = [
 ("R1_rotcontrol", 140,100, "Concrete"),
 ("R2_produce",    150,100, "Concrete"),
 ("R3_mat",        160,100, "RUT_MycelialMatting"),
 ("R4_stonetwin",  170,100, "Concrete"),
 ("R5_furnace",    180,100, "Concrete"),
 ("R6_shelter",    190,100, "Concrete"),
]
with RimBridge(host, port, token) as rb:
    for name,x,z,floor in ROOMS:
        r = rb.call("jawa/make_empty_room", {"rect":"%d,%d,7,7"%(x,z), "wallDef":"Wall","stuffDef":"Steel","doorDef":"Door","floorDef":floor,"roofDef":"RoofConstructed"})
        print(name, r.get("success"), json.dumps({k:v for k,v in r.items() if k not in ("operation",)})[:260])
