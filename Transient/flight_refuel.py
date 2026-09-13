import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def fresh(): return RimBridge(host, port, token)
time.sleep(30)
with fresh() as rb:
    tanks = rb.call("jawa/list_things", {"defName": "ChemfuelTank", "rect": "143,59,86,133", "limit": 5}).get("things", [])
    af = rb.call("jawa/list_things", {"defName": "VGE_Astrofuel", "rect": "143,59,86,133", "limit": 10}).get("things", [])
    cf = rb.call("jawa/list_things", {"defName": "Chemfuel", "rect": "143,59,86,133", "limit": 12}).get("things", [])
    print("tanks:", [t["id"] for t in tanks], "| astrofuel stacks:", len(af), "| chemfuel stacks:", len(cf))
    rb.call("rimworld/set_time_speed", {"speed": 1})
    time.sleep(0.5)
    j = rb.call("jawa/ordered_job", {"pawnId": "Human470527", "jobDef": "Refuel", "targetAId": tanks[0]["id"], "targetBId": af[0]["id"], "count": 75, "waitTicks": 400, "timeoutSeconds": 20})
    print("astrofuel attempt:", json.dumps({k: j.get(k) for k in ("success","accepted","afterJobDef","nowRunningRequested")}))
    if not j.get("nowRunningRequested"):
        j2 = rb.call("jawa/ordered_job", {"pawnId": "Human470527", "jobDef": "Refuel", "targetAId": tanks[0]["id"], "targetBId": cf[0]["id"], "count": 75, "waitTicks": 400, "timeoutSeconds": 20})
        print("chemfuel attempt:", json.dumps({k: j2.get(k) for k in ("success","accepted","afterJobDef","nowRunningRequested")}))
