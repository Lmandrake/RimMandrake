import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=15.0) as rb:
    r = rb.call("rimbridge/get_bridge_status", {})
    print(json.dumps(r)[:1200])
