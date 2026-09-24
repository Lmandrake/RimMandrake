import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    pid = "Human669116"
    r1 = rb.call("jawa/pawn_health", {"pawn": pid, "action": "add", "hediff": "Cut", "bodyPart": "Torso", "severity": 6})
    print("CUT_TORSO", r1.get("success"), r1.get("didWhat"))
    r2 = rb.call("jawa/pawn_health", {"pawn": pid, "action": "add", "hediff": "MissingBodyPart", "bodyPart": "Kidney"})
    print("MISSING_KIDNEY", r2.get("success"), r2.get("didWhat"))
    r3 = rb.call("jawa/pawn_health", {"pawn": pid, "action": "add", "hediff": "Bruise", "bodyPart": "Brain", "severity": 3})
    print("BRAIN_BRUISE", r3.get("success"), r3.get("didWhat"))
    r4 = rb.call("jawa/pawn_health", {"pawn": pid, "action": "add", "hediff": "WoundInfection", "bodyPart": "Torso", "severity": 1})
    print("INFECTION", r4.get("success"), r4.get("didWhat"))

    r5 = rb.call("jawa/ordered_job", {
        "jobDef": "EnterBuilding",
        "pawnId": pid,
        "targetAId": "RSW_BactaTank692523",
    })
    print("ORDER_ENTER", json.dumps(r5)[:1500])
