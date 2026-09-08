import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    r = rb.call("jawa/world_tile_get", {"tiles":"24"})
    d=(r.get("tiles") or [{}])[0]
    for k in ("tile","biome","elevation","temperature","rainfall","hilliness","hillinessInt","swampiness","feature"):
        print(f"  LIVE {k:14s} {d.get(k)}")
