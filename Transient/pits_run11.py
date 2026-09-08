import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=20) as rb:
    r = rb.call("rimworld/get_cell_info", {"x": 103, "z": 130})
    print(json.dumps(r.get("cell"), indent=2))
