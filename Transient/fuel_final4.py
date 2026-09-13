import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def fresh(): return RimBridge(host, port, token)
with fresh() as rb:
    # remove the possibly-forbidden stacks
    old = rb.call("jawa/list_things", {"defName": "VGE_Astrofuel", "rect": "143,59,86,133", "limit": 10}).get("things", [])
    for t in old:
        rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: Destroy", "thingId": "Thing_" + t["id"]})
    print("removed", len(old), "old stacks")
    # respawn via companion: ops "defName:x,z,count"? try ops grammar
    s = rb.call("jawa/spawn_batch", {"ops": "VGE_Astrofuel:150,148,75;VGE_Astrofuel:150,151,75;VGE_Astrofuel:151,148,75;VGE_Astrofuel:151,151,75;VGE_Astrofuel:152,148,75;VGE_Astrofuel:152,151,75"})
    print("spawn_batch:", s.get("success"), str(s.get("message",""))[:100], "spawned:", s.get("spawned", s.get("placed")))
    time.sleep(1)
    with fresh() as rb2:
        rb2.call("rimworld/set_time_speed", {"speed": 1})
        time.sleep(0.5)
        j = rb2.call("jawa/ordered_job", {"pawnId": "Human470527", "jobDef": "Refuel", "targetAId": "ChemfuelTank466253", "timeoutSeconds": 8, "waitTicks": 240})
        print("refuel (auto-fuel-find):", json.dumps({k: j.get(k) for k in ("success","accepted","afterJobDef","note")})[:300])
