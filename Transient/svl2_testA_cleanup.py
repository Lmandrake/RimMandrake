import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for tid in ["RSW_Korrum669306", "RSW_Korrum669307"]:
        r = rb.call("jawa/destroy_batch", {"ids": tid})
        print(tid, json.dumps(r)[:500])
