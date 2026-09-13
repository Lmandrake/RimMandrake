import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def fresh(): return RimBridge(host, port, token)
with fresh() as rb:
    tanks = rb.call("jawa/list_things", {"defName": "ChemfuelTank", "rect": "143,59,86,133", "limit": 5}).get("things", [])
    print("tanks now:", [(t["id"], t["x"], t["z"]) for t in tanks])
    if tanks:
        tid, fid = tanks[0]["id"], "VGE_Astrofuel470544"
        rb.call("rimworld/set_time_speed", {"speed": 1})
        j = rb.call("jawa/ordered_job", {"pawnId": "Human470527", "jobDef": "Refuel", "targetAId": tid, "targetBId": fid, "count": 75, "waitTicks": 600, "timeoutSeconds": 25})
        print("refuel:", json.dumps({k: j.get(k) for k in ("success","accepted","afterJobDef","nowRunningRequested","note")})[:250])
