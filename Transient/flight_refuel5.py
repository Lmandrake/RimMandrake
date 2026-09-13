import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def fresh(): return RimBridge(host, port, token)
with fresh() as rb:
    # spawn fuel ON the interaction cells, order forced refuel while PAUSED (reserves the stack)
    rb.call("jawa/spawn_batch", {"ops": "Chemfuel:148,147,75;Chemfuel:148,148,75;Chemfuel:148,151,75;Chemfuel:148,152,75"})
    f = rb.call("jawa/list_things", {"defName": "Chemfuel", "rect": "143,59,86,133", "limit": 8}).get("things", [])
    tanks = rb.call("jawa/list_things", {"defName": "ChemfuelTank", "rect": "143,59,86,133", "limit": 5}).get("things", [])
    print("chemfuel:", len(f), "tanks:", [t["id"] for t in tanks])
    # order while paused — reservation holds
    j1 = rb.call("jawa/ordered_job", {"pawnId": "Human470527", "jobDef": "Refuel", "targetAId": tanks[0]["id"], "targetBId": f[0]["id"], "count": 75, "timeoutSeconds": 4})
    j2 = rb.call("jawa/ordered_job", {"pawnId": "Human470533", "jobDef": "Refuel", "targetAId": tanks[1]["id"], "targetBId": f[2]["id"], "count": 75, "timeoutSeconds": 4})
    print("orders while paused:", j1.get("accepted"), j2.get("accepted"))
    rb.call("rimworld/set_time_speed", {"speed": 3})
for i in range(12):
    time.sleep(12)
    try:
        with fresh() as rb:
            r = rb.call("jawa/inspect_string", {"thingIds": "PilotConsole469283,ChemfuelTank483473,ChemfuelTank483474"})
            rows = {x.get("id"): str(x.get("inspect") or x.get("text")) for x in r.get("things", r.get("results", []))}
            con = rows.get("PilotConsole469283","")
            cf = con.split("Stored astrofuel: ")[-1].split("'")[0][:9] if "Stored astrofuel" in con else "?"
            rng = con.split("Gravship range: ")[-1].split("'")[0].strip()[:5] if "Gravship range" in con else "?"
            t1 = rows.get("ChemfuelTank483473",""); f1 = t1.split(" stored: ")[-1].split(" l")[0][:8] if " stored" in t1 else "gone"
            print(f"t+{(i+1)*12}s console={cf} tank1={f1} RANGE={rng}", flush=True)
            if rng and rng.split() and rng.split()[0].isdigit() and int(rng.split()[0]) >= 18:
                print("FUELED", flush=True); break
    except Exception as e:
        print("probe:", str(e)[:50], flush=True)
with fresh() as rb:
    rb.call("rimworld/set_time_speed", {"speed": 0})
    print("paused", flush=True)
