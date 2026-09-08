import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for x in range(70, 100):
        for z in range(84, 91):
            ci = rb.call("rimworld/get_cell_info", {"x": x, "z": z}).get("cell", {})
            names = [t.get("defName") for t in ci.get("things", []) if t.get("defName","").startswith("AB_")]
            if names:
                print(x, z, names)
