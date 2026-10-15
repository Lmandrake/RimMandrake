import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t,timeout=120.0) as rb:
    r = rb.call("jawa/list_pawns", {"limit": 1000})
    wild = [x for x in r.get("pawns") or [] if x.get("faction") is None and x.get("intelligence") == "Animal" and not x.get("dead")]
    print("wild", len(wild), sorted({x.get("kindDef") for x in wild}))
