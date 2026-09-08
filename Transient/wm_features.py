import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    r = rb.call("jawa/world_features_get", {"limit": 100})
    fs = r.get("features") or r.get("objects") or []
    print("features:", len(fs))
    fs2 = sorted(fs, key=lambda f: -(f.get("maxDrawSizeInTiles") or 0))
    for f in fs2[:12]:
        print(f"  {(f.get('name') or '?'):24.24} size={f.get('maxDrawSizeInTiles')}")
    vals=[f.get("maxDrawSizeInTiles") or 0 for f in fs]
    if vals: print(f"  MEASURED max={max(vals):.1f} min={min(vals):.1f} mean={sum(vals)/len(vals):.1f}")
