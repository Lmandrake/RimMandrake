import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def fresh(): return RimBridge(host, port, token)
with fresh() as rb:
    fuel = rb.call("jawa/list_things", {"defName": "VGE_Astrofuel", "rect": "143,59,86,133", "limit": 10}).get("things", [])
    print("fuel:", [(t["id"], t.get("stackCount")) for t in fuel])
    rb.call("rimworld/set_time_speed", {"speed": 1})
    time.sleep(0.5)
    j = rb.call("jawa/ordered_job", {"pawnId": "Human470527", "jobDef": "Refuel", "targetAId": "ChemfuelTank466253", "targetBId": fuel[0]["id"], "waitTicks": 300, "timeoutSeconds": 15})
    print("refuel:", json.dumps({k: j.get(k) for k in ("success","accepted","afterJobDef","nowRunningRequested","note")})[:280])
