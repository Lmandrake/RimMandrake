import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/order_pawn", {"pawnId": "Human470527", "targetId": "ChemfuelTank470550", "pathEndMode": "Touch", "timeoutSeconds": 6})
    print(json.dumps({k: r.get(k) for k in ("success","canReach","accepted","message","note")})[:250])
    p = rb.call("jawa/list_pawns", {"faction": "PlayerColony", "limit": 6})
    for c in p.get("pawns", []): print(c["id"], c.get("name"), "at", c.get("x"), c.get("z"))
    f = rb.call("jawa/list_things", {"defName": "VGE_Astrofuel", "rect": "143,59,86,133", "limit": 2}).get("things", [])
    r2 = rb.call("jawa/order_pawn", {"pawnId": "Human470527", "targetId": f[0]["id"], "pathEndMode": "Touch", "timeoutSeconds": 6})
    print("to fuel:", json.dumps({k: r2.get(k) for k in ("success","canReach","message")})[:200])
