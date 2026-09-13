import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("rimworld/set_time_speed", {"speed": 1})
    time.sleep(0.3)
    j = rb.call("jawa/ordered_job", {"pawnId": "Human470527", "jobDef": "HaulToCell", "targetAId": "VGE_Astrofuel470544", "targetBX": 152, "targetBZ": 150, "count": 10, "waitTicks": 120, "timeoutSeconds": 10})
    print(json.dumps({k: j.get(k) for k in ("success","accepted","beforeJobDef","afterJobDef","nowRunningRequested","note","message")})[:400])
