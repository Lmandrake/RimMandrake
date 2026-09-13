import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def fresh(): return RimBridge(host, port, token)
with fresh() as rb:
    for mid in ("MinifiedThing74107", "MinifiedThing74108"):
        rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: Destroy", "thingId": "Thing_" + mid})
    b = rb.call("jawa/build_batch", {"ops": "ChemfuelTank:149,148,0;ChemfuelTank:149,151,0", "faction": "player", "readBack": 2})
    print("build:", b.get("success"), "placed:", b.get("placed"), str(b.get("failed",""))[:120])
    rb.call("jawa/map_commit", {})
    tanks = rb.call("jawa/list_things", {"defName": "ChemfuelTank", "rect": "143,59,86,133", "limit": 5}).get("things", [])
    print("tanks:", [(t["id"], t["x"], t["z"], t.get("faction")) for t in tanks])
    if len(tanks) == 2:
        fuel = rb.call("jawa/list_things", {"defName": "VGE_Astrofuel", "rect": "143,59,86,133", "limit": 10}).get("things", [])
        rb.call("rimworld/set_time_speed", {"speed": 1})
        time.sleep(0.3)
        jobs = [("Human470527", tanks[0]["id"], fuel[0]["id"]), ("Human470533", tanks[1]["id"], fuel[1]["id"]),
                ("Human470524", "PilotConsole469283", fuel[2]["id"])]
        for pid, tgt, f in jobs:
            j = rb.call("jawa/ordered_job", {"pawnId": pid, "jobDef": "Refuel", "targetAId": tgt, "targetBId": f, "count": 75, "timeoutSeconds": 8})
            print(pid, "->", tgt, ":", j.get("success"), j.get("accepted"), str(j.get("note",""))[:60])
