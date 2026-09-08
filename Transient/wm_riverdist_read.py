import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    r = rb.call("jawa/world_links_get", {"tiles": "19369,2014,19366,6449,18413,1855,18411,8334,8330,8331"})
    print(json.dumps(r)[:2500])
