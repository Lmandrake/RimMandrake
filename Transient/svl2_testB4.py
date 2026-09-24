import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    lt = rb.call("jawa/list_things", {"rect": "0,0,100,100", "limit": 30})
    print(json.dumps(lt)[:3000])
