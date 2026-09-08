import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    r = rb.call("jawa/map_fire", {"action":"start","rect":"140,132,6,6","fireSize":1.2})
    print("FIRE RESULT:", json.dumps(r)[:600])
    r2 = rb.call("jawa/drain_log", {"contains": "Ninefold] ", "limit": 50})
    for m in r2.get("messages", []):
        print(m["text"])
