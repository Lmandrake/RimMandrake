import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
APPLY = "--apply" in sys.argv
with RimBridge(h,p,t) as rb:
    r = rb.call("jawa/world_links_import", {
        "path": r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_links.csv",
        "clearFirst": True, "apply": APPLY})
    print(("APPLY" if APPLY else "DRY"), json.dumps(r)[:500])
