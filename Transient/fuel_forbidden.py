import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ci = rb.call("rimworld/get_cell_info", {"x": 150, "z": 148})
    print(json.dumps(ci.get("things", []), indent=1)[:600])
