import sys, json, os
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
print("endpoint", host, port, (token or "")[:8])
with RimBridge(host, port, token) as rb:
    r = rb.call("rimbridge/get_bridge_status", {})
    print("status", json.dumps(r)[:600])
