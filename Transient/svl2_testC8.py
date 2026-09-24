import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/connect_cells", {"from": "172,139", "to": "170,138", "thing": "PowerConduit", "mode": "mine", "dryRun": False})
    print("CONNECT", json.dumps(r)[:1500])
