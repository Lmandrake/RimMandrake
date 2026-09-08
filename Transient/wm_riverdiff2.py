import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    r = rb.call("jawa/world_links_validate",
                {"path": r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_links.csv", "limit": 40})
    for k,v in r.items():
        if k in ("operation",): continue
        if isinstance(v, list):
            print(f"{k}: {len(v)}", json.dumps(v[:6])[:300])
        else:
            print(f"{k}: {v}")
