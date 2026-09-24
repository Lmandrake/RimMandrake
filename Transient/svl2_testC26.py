import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    pid = "RSW_Dewback669123"
    r1 = rb.call("jawa/pawn_health", {"pawn": pid, "action": "add", "hediff": "Cut", "severity": 6})
    print("CUT_NOBODYPART", json.dumps(r1)[:600])
    lp = rb.call("jawa/list_pawns", {})
    still_there = any(p.get("id") == pid for p in lp.get("pawns", []))
    print("STILL_THERE", still_there)
