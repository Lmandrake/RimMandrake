import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    r = rb.call("jawa/drain_log", {"contains": "Ninefold] ", "limit": 500})
    msgs = r.get("messages", [])
    print("count:", len(msgs), "totalInBuffer:", r.get("totalInBuffer"))
    for m in msgs:
        print(m["text"])
