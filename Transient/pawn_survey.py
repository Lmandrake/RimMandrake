import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
rb = RimBridge(host=host, port=port, token=token).connect()

lp = rb.call("jawa/list_pawns", {"limit": 500})
pawns = lp.get("pawns", [])
print("total pawns:", len(pawns))
for p in pawns:
    print(json.dumps(p))
