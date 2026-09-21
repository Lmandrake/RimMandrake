import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
CENTERS = {"R1_rotcontrol":(143,103),"R2_produce":(153,103),"R3_mat":(163,103),"R4_stonetwin":(173,103),"R5_furnace":(183,103),"R6_shelter":(193,103)}
with RimBridge(host, port, token) as rb:
    for n,(x,z) in CENTERS.items():
        r = rb.call("jawa/room_get", {"x":x,"z":z})
        rooms = r.get("rooms") or []
        rm = rooms[0] if rooms else {}
        t = rb.call("jawa/cell_temperature", {"cell":"%d,%d"%(x,z)})
        ci = rb.call("rimworld/get_cell_info", {"x":x,"z":z})
        print(n, "| cells", rm.get("cellCount"), "outdoor?", rm.get("usesOutdoorTemperature"), "roofed", rm.get("openRoofCount"), "temp", rm.get("temperature"),
              "| cellTemp", t.get("temperature"), "outdoorTemp", t.get("outdoorTemp"),
              "| terrain", ci.get("terrain") or ci.get("terrainDefName"), "roof", ci.get("roof") or ci.get("roofDefName"))
