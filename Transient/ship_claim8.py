import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    cats = rb.call("rimworld/list_architect_categories", {})
    names = [c.get("id") or c.get("defName") for c in (cats.get("categories") or [])]
    print("categories:", names[:20])
    target = next((n for n in names if "order" in str(n).lower()), None)
    print("orders cat:", target)
    if target:
        r = rb.call("rimworld/list_architect_designators", {"categoryId": target})
        for d in (r.get("designators") or []):
            if "claim" in str(d).lower(): print("CLAIM:", d)
