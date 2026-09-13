import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def fresh(): return RimBridge(host, port, token)
with fresh() as rb:
    rb.call("rimworld/set_time_speed", {"speed": 1})
    time.sleep(1)
    f = rb.call("jawa/list_things", {"defName": "VGE_Astrofuel", "rect": "143,59,86,133", "limit": 3}).get("things", [])
    j = rb.call("jawa/ordered_job", {"pawnId": "Human470533", "jobDef": "Refuel", "targetAId": "ChemfuelTank470550", "targetBId": f[0]["id"], "count": 75, "waitTicks": 600, "timeoutSeconds": 25})
    print(json.dumps({k: j.get(k) for k in ("success","accepted","beforeJobDef","afterJobDef","nowRunningRequested","ticksElapsed")}))
time.sleep(15)
with fresh() as rb:
    r = rb.call("jawa/inspect_string", {"thingIds": "ChemfuelTank470550"})
    print(str([x.get("inspect") or x.get("text") for x in r.get("things", r.get("results", []))])[:160])
    rb.call("rimworld/set_time_speed", {"speed": 0})
