import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    pid = "RSW_Dewback669123"
    r4 = rb.call("jawa/pawn_health", {"pawn": pid, "action": "add", "hediff": "WoundInfection", "bodyPart": "Body", "severity": 1})
    print("INFECTION", r4.get("success"), r4.get("didWhat"))
    lp = rb.call("jawa/list_pawns", {})
    print("STILL_THERE", any(p.get("id") == pid for p in lp.get("pawns", [])))
