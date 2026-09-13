import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    j = rb.call("jawa/ordered_job", {"pawnId": "Human470527", "jobDef": "Refuel", "targetAId": "ChemfuelTank466253", "targetBId": "VGE_Astrofuel470544", "count": 75, "timeoutSeconds": 15})
    print(json.dumps(j, indent=1)[:900])
