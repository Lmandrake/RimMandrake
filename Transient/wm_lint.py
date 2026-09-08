import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    r = rb.call("jawa/world_lint", {"limit": 5})
    print("total:", r.get("totalFindings"))
    for k,v in (r.get("checks") or {}).items():
        c=v.get("count",0)
        if c: print(f"  {c:6d}  {k}  ex={v.get('examples')[:4] if v.get('examples') else []}")
