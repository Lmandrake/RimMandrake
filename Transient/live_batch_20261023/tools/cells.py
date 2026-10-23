"""cells.py MAPID X0 Z0 X1 Z1 -- dump non-trivial cell contents"""
import sys, json, time
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
mid,x0,z0,x1,z1 = map(int, sys.argv[1:6])
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    if mid >= 0:
        rb.call("jawa/set_current_map", {"mapId": mid}); time.sleep(0.5)
    for z in range(z1, z0-1, -1):
        for x in range(x0, x1+1):
            r = rb.call("rimworld/get_cell_info", {"x": x, "z": z}).get("cell", {})
            th = r.get("things") or []
            ts = [ (t.get("defName"), t.get("thingId") or t.get("id")) for t in th]
            print(x, z, r.get("terrainDefName") or r.get("terrain"), ts)
