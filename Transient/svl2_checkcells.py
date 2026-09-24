import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for (x,z) in [(230,230),(190,140)]:
        ci = rb.call("rimworld/get_cell_info", {"x": x, "z": z})
        print(x, z, json.dumps(ci.get("cell"))[:500])
