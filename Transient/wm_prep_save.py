import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    v = rb.call("jawa/world_objects_validate", {})
    print("VALIDATE:", json.dumps(v)[:900]); print()
