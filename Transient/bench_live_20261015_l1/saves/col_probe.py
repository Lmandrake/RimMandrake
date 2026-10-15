import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t,timeout=120.0) as rb:
    r = rb.call("jawa/list_pawns", {"limit": 500})
    for x in r.get("pawns") or []:
        if x.get("isPlayer") and x.get("intelligence") == "Humanlike":
            print({k: x.get(k) for k in ("id","dead","downed","health","summaryHealth","x","z")})
