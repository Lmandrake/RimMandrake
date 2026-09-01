import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for act in ("get","read","count","query"):
        h = rb.call("jawa/pawn_health", {"pawn": "Thrumbo79608", "hediff": "Gunshot", "action": act})
        if h.get("success"):
            print(act, "->", json.dumps({k:h.get(k) for k in ("didWhat","hediffCount","hediffs")})[:400]); break
        else:
            print(act, "refused:", h.get("message"))
