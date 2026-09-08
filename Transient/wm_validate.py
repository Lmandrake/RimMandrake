import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

CSV = r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv"

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/world_tile_validate", {"path": CSV, "limit": 200, "maxRows": 0})
    d = {k: v for k, v in r.items() if k != "operation"}
    diffs = d.pop("diffs", None) or d.pop("rows", None)
    print("== summary ==")
    print(json.dumps(d, indent=1)[:3000])
    if diffs:
        print("\n== first diffs (%d shown) ==" % len(diffs))
        for x in diffs[:60]:
            print(json.dumps(x))
