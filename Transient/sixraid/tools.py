import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call_raw("tools/list", {}) if hasattr(rb, "call_raw") else None
    print(type(rb), [m for m in dir(rb) if not m.startswith("_")])
