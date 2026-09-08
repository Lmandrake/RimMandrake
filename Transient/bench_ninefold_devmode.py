import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    r = rb.call("jawa/prefs", {"devMode": True})
    print("SET:", json.dumps(r)[:500])
    r2 = rb.call("jawa/prefs", {})
    print("READBACK:", json.dumps(r2)[:500])
