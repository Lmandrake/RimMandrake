import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

OUT = r"D:\Luke\dev\Rimworld\Transient\live_tiles_export.csv"
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    tl = {t["name"]: t for t in rb.list_tools()}
    print("export schema:", json.dumps(tl["jawa/world_tile_export"].get("inputSchema"))[:500])
    r = rb.call("jawa/world_tile_export", {"path": OUT})
    print(json.dumps({k: v for k, v in r.items() if k != "operation"})[:600])
