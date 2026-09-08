import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    for args in ({"tiles":"16869"},{"tiles":"24"}):
        try:
            r=rb.call("jawa/world_objects_get", args)
            print(args, "->", json.dumps(r)[:500]); print()
        except Exception as e:
            print(args,"!!",type(e).__name__,str(e)[:200]); print()
