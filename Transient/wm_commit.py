import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    print("commit:", json.dumps(rb.call("jawa/world_commit", {}))[:200])
    r = rb.call("jawa/world_links_validate", {"limit": 5})
    print("riverEntries:", r.get("riverEntries"), " riverTiles:", r.get("riverTiles"),
          " roadEntries:", r.get("roadEntries"), " hiddenByBiome:", r.get("hiddenByBiomeCount"))
