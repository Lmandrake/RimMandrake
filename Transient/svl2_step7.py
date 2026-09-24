import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for (x, z) in [(200, 200), (230, 230), (10, 200), (200, 10), (5,5), (240,240)]:
        ci = rb.call("rimworld/get_cell_info", {"x": x, "z": z})
        print(x, z, json.dumps(ci)[:400])
