import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    r = rb.call("jawa/world_tile_import",
                {"path": r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv", "apply": True})
    print("tiles:", json.dumps(r)[:300]); print()
    print("commit:", json.dumps(rb.call("jawa/world_commit", {}))[:120])
