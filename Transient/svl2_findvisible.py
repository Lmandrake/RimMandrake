import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for (x, z) in [(190,140),(185,138),(195,145),(200,150),(180,140),(175,130),(176,138)]:
        ci = rb.call("rimworld/get_cell_info", {"x": x, "z": z})
        c = ci.get("cell", {})
        print(x, z, "fogged=", c.get("fogged"), "walkable=", c.get("walkable"), "terrain=", c.get("terrainDefName"))
