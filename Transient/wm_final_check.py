import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    v = rb.call("jawa/world_links_validate", {"limit": 2})
    print("riverEntries:", v.get("riverEntries"), "(want 584)  riverTiles:", v.get("riverTiles"),
          "(want 308)  asym:", v.get("asymmetricCount"), " roads:", v.get("roadEntries"))
    e = rb.call("jawa/world_tile_export", {"path": r"D:\Luke\dev\Rimworld\Transient\wm_readback_v4.csv"})
    print("export:", e.get("tilesTotal"), "tiles")
