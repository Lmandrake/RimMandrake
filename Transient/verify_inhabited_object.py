import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/world_objects_get", {"tiles": "20000"})
    print(json.dumps(r, indent=2))
