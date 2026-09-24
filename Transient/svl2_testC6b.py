import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for (x,z) in [(171,140),(171,141),(171,138)]:
        ci = rb.call("rimworld/get_cell_info", {"x": x, "z": z})
        c = ci.get("cell", {})
        print(x, z, "terrain=", c.get("terrainDefName"), "walkable=", c.get("walkable"), "things=", c.get("solidThingDefs"))
