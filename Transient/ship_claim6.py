import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("rimworld/list_architect_designators", {})
    rows = r.get("designators") or r.get("items") or []
    hits = [d for d in rows if "claim" in str(d).lower()]
    print(hits[:3])
