import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    res = rb.call("jawa/build_batch", {"ops": "Dirt_Hill_Right:200,200"})
    print("build result:", json.dumps(res)[:500])
    ci = rb.call("rimworld/get_cell_info", {"x": 200, "z": 200}).get("cell", {})
    print("cell after:", ci.get("terrainDefName"), [t.get("defName") for t in ci.get("things",[])])
