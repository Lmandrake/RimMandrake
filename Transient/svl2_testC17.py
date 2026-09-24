import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/ordered_job", {
        "jobDef": "Refuel",
        "pawnId": "Human692499",
        "targetAId": "RSW_BactaTank692523",
        "targetBId": "RSW_Bacta692528",
        "count": 25,
    })
    print("ORDER_REFUEL", json.dumps(r)[:2000])
