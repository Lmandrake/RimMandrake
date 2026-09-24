import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    # fresh wound - torso
    r1 = rb.call("jawa/pawn_health", {"pawn": "Human692499", "action": "add", "hediff": "Cut", "bodyPart": "Torso", "severity": 6})
    print("CUT_TORSO", json.dumps(r1)[:500])
    # missing organ - kidney
    r2 = rb.call("jawa/pawn_health", {"pawn": "Human692499", "action": "add", "hediff": "MissingBodyPart", "bodyPart": "Kidney"})
    print("MISSING_KIDNEY", json.dumps(r2)[:500])
    # brain injury
    r3 = rb.call("jawa/pawn_health", {"pawn": "Human692499", "action": "add", "hediff": "Bruise", "bodyPart": "Brain", "severity": 3})
    print("BRAIN_BRUISE", json.dumps(r3)[:500])
    # infection
    r4 = rb.call("jawa/pawn_health", {"pawn": "Human692499", "action": "add", "hediff": "WoundInfection", "bodyPart": "Torso", "severity": 1})
    print("INFECTION", json.dumps(r4)[:500])
