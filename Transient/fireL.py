import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("rimworld/execute_debug_action", {"path": "Actions\\Mental state...\\ManhunterPermanent", "pawnId": "Thing_Thrumbo79608"})
    print("via pawnId:", r.get("success"), str(r.get("message") or "")[:80])
    if not r.get("success"):
        try:
            rb.call("jawa/order_pawn", {"bogus":1})
        except Exception as e:
            print("order_pawn declared:", str(e).split("Declared:")[-1].strip()[:120])
