import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for x, z in [(87,87),(85,87),(90,87),(84,86),(91,88),(83,87),(82,87),(80,86),(78,86)]:
        ci = rb.call("rimworld/get_cell_info", {"x": x, "z": z}).get("cell", {})
        print(x, z, [t.get("defName") for t in ci.get("things", [])])
