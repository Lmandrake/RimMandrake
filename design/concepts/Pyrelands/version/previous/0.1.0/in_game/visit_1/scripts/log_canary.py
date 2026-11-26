import sys, re
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,tk = resolve_endpoint()
with RimBridge(h,p,tk) as rb:
    mark=rb.call("jawa/drain_log",{"limit":1}).get("totalInBuffer")
    w=rb.call("jawa/static_call",{"type":"Verse.Log","method":"Warning","args":"visit1 canary: the fire rite begins"}); print("log call", w.get("success"), str(w.get("message") or w.get("result"))[:120])
    r=rb.call("jawa/drain_log",{"limit":500}); total=r.get("totalInBuffer"); msgs=r.get("messages") or []
    new=msgs[len(msgs)-(total-mark):] if total>mark else []
    print("mark", mark, "total", total, "window", [m.get("text")[:80] for m in new], "matches", [bool(re.search(r"\brites?\b|FireRite|RiteHook", m.get("text",""), re.I)) for m in new])
