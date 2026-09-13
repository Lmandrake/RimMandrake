import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    p = rb.call("jawa/list_pawns", {"faction": "PlayerColony", "limit": 20})
    print("player pawns:", len(p.get("pawns", [])))
    for x in p.get("pawns", []):
        print(" ", x.get("id"), "|", x.get("name") or x.get("label"), "at", x.get("x"), x.get("z"), "downed:", x.get("downed"))
