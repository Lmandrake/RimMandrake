import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/list_things", {"rect": "173,138,1,1", "limit": 5, "defName": "RSW_Bacta"})
    print(json.dumps(r)[:1200])
