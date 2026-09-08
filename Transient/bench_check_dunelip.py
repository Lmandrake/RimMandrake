import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for x in range(120, 145):
        for z in range(30, 46):
            ci = rb.call("rimworld/get_cell_info", {"x": x, "z": z}).get("cell", {})
            names = [t.get("defName") for t in ci.get("things", []) if "Hill" in t.get("defName","") or "Truck" in t.get("defName","")]
            if names:
                print(x, z, names)
