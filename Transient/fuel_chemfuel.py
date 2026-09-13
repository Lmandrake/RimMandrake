import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def fresh(): return RimBridge(host, port, token)
with fresh() as rb:
    s = rb.call("jawa/spawn_batch", {"ops": "Chemfuel:152,149,75;Chemfuel:152,150,75;Chemfuel:153,149,75;Chemfuel:153,150,75;Chemfuel:154,149,75;Chemfuel:154,150,75;Chemfuel:155,149,75;Chemfuel:155,150,75"})
    print("chemfuel:", s.get("success"), s.get("message","")[:60])
    fuel = rb.call("jawa/list_things", {"defName": "Chemfuel", "rect": "143,59,86,133", "limit": 12}).get("things", [])
    tanks = rb.call("jawa/list_things", {"defName": "ChemfuelTank", "rect": "143,59,86,133", "limit": 5}).get("things", [])
    rb.call("rimworld/set_time_speed", {"speed": 2})
    time.sleep(0.3)
    jobs = [("Human470527", tanks[0]["id"], fuel[0]["id"]), ("Human470533", tanks[1]["id"], fuel[1]["id"]), ("Human470524", "PilotConsole469283", fuel[2]["id"])]
    for pid, tgt, f in jobs:
        j = rb.call("jawa/ordered_job", {"pawnId": pid, "jobDef": "Refuel", "targetAId": tgt, "targetBId": f, "count": 75, "timeoutSeconds": 8})
        print(pid, "->", tgt, ":", j.get("success"), j.get("afterJobDef"))
for i in range(15):
    time.sleep(10)
    try:
        with fresh() as rb:
            r = rb.call("jawa/inspect_string", {"thingIds": "PilotConsole469283,ChemfuelTank470550,ChemfuelTank470551"})
            rows = {x.get("id"): str(x.get("inspect") or x.get("text")) for x in r.get("things", r.get("results", []))}
            con = rows.get("PilotConsole469283","")
            cf = con.split("Stored astrofuel: ")[-1].split("'")[0][:9] if "Stored astrofuel" in con else "?"
            rng = con.split("Gravship range: ")[-1].split("'")[0][:5] if "Gravship range" in con else "?"
            t1 = rows.get("ChemfuelTank470550",""); f1 = t1.split(" stored: ")[-1].split(" l'")[0][:9] if " stored" in t1 else "?"
            t2 = rows.get("ChemfuelTank470551",""); f2 = t2.split(" stored: ")[-1].split(" l'")[0][:9] if " stored" in t2 else "?"
            print(f"t+{(i+1)*10}s console={cf} tank1={f1} tank2={f2} RANGE={rng}", flush=True)
            if rng.strip().split()[0].isdigit() and int(rng.strip().split()[0]) >= 16:
                print("RANGE SUFFICIENT", flush=True); break
    except Exception as e:
        print("probe:", str(e)[:50], flush=True)
with fresh() as rb:
    rb.call("rimworld/set_time_speed", {"speed": 0})
print("paused", flush=True)
