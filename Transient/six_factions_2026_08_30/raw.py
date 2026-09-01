import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/drain_log", {"limit":4, "contains":"Hostile group incoming"})
    print(json.dumps(r, indent=1, ensure_ascii=False)[:1500])
