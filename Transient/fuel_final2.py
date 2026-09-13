import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def fresh(): return RimBridge(host, port, token)
with fresh() as rb:
    rb.call("rimworld/set_time_speed", {"speed": 1})
    j = rb.call("jawa/ordered_job", {"pawnId": "Human470527", "jobDef": "Refuel", "targetAId": "ChemfuelTank466253", "targetBId": "VGE_Astrofuel469284", "timeoutSeconds": 10})
    print("refuel order FULL:", json.dumps(j)[:500])
