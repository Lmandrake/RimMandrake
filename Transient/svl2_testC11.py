import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/container_fill", {"thing": "RSW_BactaTank692523", "items": "RSW_Bacta:30"})
    print("FILL", json.dumps(r)[:2000])
