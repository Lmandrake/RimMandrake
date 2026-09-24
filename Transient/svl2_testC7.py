import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/build_batch", {"ops": "RSW_BactaTank:171,139,0"})
    print("BUILD_TANK", json.dumps(r)[:2500])
