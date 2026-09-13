import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def fresh(): return RimBridge(host, port, token)
with fresh() as rb:
    f = rb.call("jawa/list_things", {"defName": "VGE_Astrofuel", "rect": "143,59,86,133", "limit": 6}).get("things", [])
    tanks = rb.call("jawa/list_things", {"defName": "ChemfuelTank", "rect": "143,59,86,133", "limit": 5}).get("things", [])
    rb.call("rimworld/set_time_speed", {"speed": 3})
    jobs = [("Human470527", tanks[0]["id"], f[0]["id"]), ("Human470533", tanks[1]["id"], f[1]["id"]),
            ("Human470524", "PilotConsole469283", f[2]["id"]), ("Human470521", "PilotConsole469283", f[3]["id"])]
    for pid, tgt, fu in jobs:
        j = rb.call("jawa/ordered_job", {"pawnId": pid, "jobDef": "Refuel", "targetAId": tgt, "targetBId": fu, "count": 75, "timeoutSeconds": 6})
        print(pid, "->", tgt, ":", j.get("afterJobDef"), j.get("nowRunningRequested"))
for i in range(16):
    time.sleep(12)
    try:
        with fresh() as rb:
            r = rb.call("jawa/inspect_string", {"thingIds": "PilotConsole469283,ChemfuelTank470550,ChemfuelTank470551"})
            rows = {x.get("id"): str(x.get("inspect") or x.get("text")) for x in r.get("things", r.get("results", []))}
            con = rows.get("PilotConsole469283","")
            cf = con.split("Stored astrofuel: ")[-1].split("'")[0][:9] if "Stored astrofuel" in con else "?"
            rng = con.split("Gravship range: ")[-1].split("'")[0].strip()[:5] if "Gravship range" in con else "?"
            t1 = rows.get("ChemfuelTank470550",""); f1 = t1.split(" stored: ")[-1].split(" l")[0][:8] if " stored" in t1 else "?"
            print(f"t+{(i+1)*12}s console_fuel={cf} tank1={f1} RANGE={rng}", flush=True)
            if rng and rng.split()[0].isdigit() and int(rng.split()[0]) >= 20:
                print("FUELED — range sufficient", flush=True); break
    except Exception as e:
        print("probe:", str(e)[:50], flush=True)
with fresh() as rb:
    rb.call("rimworld/set_time_speed", {"speed": 0})
    print("paused", flush=True)
