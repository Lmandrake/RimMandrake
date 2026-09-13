import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def fresh(): return RimBridge(host, port, token)
with fresh() as rb:
    r = rb.call("jawa/ordered_job", {"pawnId": "Human922", "jobDef": "InspectGravEngine", "targetAId": "GravEngine466248", "timeoutSeconds": 5})
    print("inspect job:", r.get("success"), str(r.get("message",""))[:120])
    # refuel jobs: Refuel jobDef, target tank + fuel
    r2 = rb.call("jawa/ordered_job", {"pawnId": "Human929", "jobDef": "Refuel", "targetAId": "ChemfuelTank466253", "targetBId": "VGE_Astrofuel469284", "count": 75, "timeoutSeconds": 5})
    print("refuel1:", r2.get("success"), str(r2.get("message",""))[:120])
    r3 = rb.call("jawa/ordered_job", {"pawnId": "Human925", "jobDef": "Refuel", "targetAId": "PilotConsole469283", "targetBId": "VGE_Astrofuel469285", "count": 75, "timeoutSeconds": 5})
    print("refuel-console:", r3.get("success"), str(r3.get("message",""))[:120])
    rb.call("rimworld/set_time_speed", {"speed": 3})
for i in range(15):
    time.sleep(10)
    try:
        with fresh() as rb:
            r = rb.call("jawa/inspect_string", {"thingIds": "ChemfuelTank466253,GravEngine466248,PilotConsole469283"})
            rows = {x.get("id"): str(x.get("inspect") or x.get("text")) for x in r.get("things", r.get("results", []))}
            eng = rows.get("GravEngine466248",""); con = rows.get("PilotConsole469283",""); t1 = rows.get("ChemfuelTank466253","")
            ins = "NEEDS-INSPECT" if "inspect" in eng.lower() else "INSPECTED"
            cf = con.split("Stored astrofuel: ")[-1].split("'")[0][:10] if "Stored astrofuel" in con else "?"
            f1 = t1.split("Astrofuel stored: ")[-1].split(" l'")[0][:10] if "Astrofuel stored" in t1 else "?"
            rng = con.split("Gravship range: ")[-1].split("'")[0][:5] if "Gravship range" in con else "?"
            print(f"t+{(i+1)*10}s {ins} console={cf} tank1={f1} range={rng}", flush=True)
            if ins == "INSPECTED" and cf[:1] not in "0?":
                print("READY", flush=True); break
    except Exception as e:
        print("probe:", str(e)[:50], flush=True)
with fresh() as rb:
    rb.call("rimworld/set_time_speed", {"speed": 0})
    print("paused", flush=True)
