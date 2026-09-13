import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/world_tile_export", {"path": r"D:\Luke\dev\Rimworld\Transient\v24_tiles_live.csv"})
    print(json.dumps(r)[:300])
