import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    r = rb.call("jawa/explosion_at", {"at":"150,150","radius":2.5,"damAmount":30,"damType":"Bomb"})
    print("EXPL RESULT:", json.dumps(r)[:400])
    r2 = rb.call("jawa/drain_log", {"contains": "Ninefold] ", "limit": 50})
    msgs = r2.get("messages", [])
    for m in msgs[-6:]:
        print(m["text"])
