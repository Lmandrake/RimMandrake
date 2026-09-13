import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    f = rb.call("jawa/world_features_get", {"limit": 100})
    names = [x.get("name") for x in f.get("features", [])]
    print("live features:", len(names))
    for n in sorted(n for n in names if n): print("  ", n)
