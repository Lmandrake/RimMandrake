import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ts = rb.call("rimbridge/list_tools", {}) if False else None
    # list tools
    try:
        r = rb.call("rimbridge/get_bridge_status", {})
        print("STATUS", json.dumps(r, indent=1)[:1200])
    except Exception as e:
        print("statuserr", e)
