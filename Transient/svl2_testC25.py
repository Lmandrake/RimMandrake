import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    pid = "RSW_Dewback669123"
    r1 = rb.call("jawa/pawn_health", {"pawn": pid, "action": "add", "hediff": "Cut", "bodyPart": "Torso", "severity": 6})
    print("CUT_TORSO", r1.get("success"), r1.get("didWhat"))
    lp = rb.call("jawa/list_pawns", {})
    still_there = any(p.get("id") == pid for p in lp.get("pawns", []))
    print("STILL_THERE_AFTER_CUT", still_there, "total=", len(lp.get("pawns", [])))
