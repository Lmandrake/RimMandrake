import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
rb = RimBridge(host=host, port=port, token=token).connect()
r = rb.call("jawa/pawn_get", {"pawn": "Human822690"})
print(json.dumps(r, indent=1)[:2500])
