import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
host_cells = [(183,150),(184,150),(183,148),(184,152),(190,150),(183,146)]
with RimBridge(host, port, token) as rb:
    # find a free foundation cell near the engine
    for x, z in host_cells:
        ci = rb.call("rimworld/get_cell_info", {"x": x, "z": z})
        th = [t.get("defName") for t in ci.get("things", [])]
        print((x,z), ci.get("terrainDefName"), th)
    # place on first empty-looking cell
