import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    pid = "AA_Eyeling669122"
    r1 = rb.call("jawa/pawn_health", {"pawn": pid, "action": "add", "hediff": "Cut", "severity": 4})
    print("CUT", json.dumps(r1)[:700])
    lp = rb.call("jawa/list_pawns", {})
    print("STILL_THERE", any(p.get("id") == pid for p in lp.get("pawns", [])))
