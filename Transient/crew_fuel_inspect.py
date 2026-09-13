import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def fresh(): return RimBridge(host, port, token)
with fresh() as rb:
    r = rb.call("jawa/pawn_traits", {"pawn": "Human470521", "action": "add", "trait": "Nerves", "degree": 2, "force": True})
    print("Captain Nerves+2 (iron-willed):", r.get("success"))
    j1 = rb.call("jawa/ordered_job", {"pawnId": "Human470521", "jobDef": "InspectGravEngine", "targetAId": "GravEngine466248", "timeoutSeconds": 5})
    print("Captain inspects:", j1.get("success"), str(j1.get("message",""))[:80])
    j2 = rb.call("jawa/ordered_job", {"pawnId": "Human470527", "jobDef": "Refuel", "targetAId": "PilotConsole469283", "targetBId": "VGE_Astrofuel469284", "count": 75, "timeoutSeconds": 5})
    print("Hands refuels console:", j2.get("success"), str(j2.get("message",""))[:80])
    j3 = rb.call("jawa/ordered_job", {"pawnId": "Human470533", "jobDef": "Refuel", "targetAId": "ChemfuelTank466253", "targetBId": "VGE_Astrofuel469285", "count": 75, "timeoutSeconds": 5})
    print("Twice-Kin refuels tank:", j3.get("success"), str(j3.get("message",""))[:80])
    rb.call("rimworld/set_time_speed", {"speed": 2})
for i in range(18):
    time.sleep(10)
    try:
        with fresh() as rb:
            r = rb.call("jawa/inspect_string", {"thingIds": "GravEngine466248,PilotConsole469283,ChemfuelTank466253"})
            rows = {x.get("id"): str(x.get("inspect") or x.get("text")) for x in r.get("things", r.get("results", []))}
            eng, con, t1 = rows.get("GravEngine466248",""), rows.get("PilotConsole469283",""), rows.get("ChemfuelTank466253","")
            ins = "NEEDS-INSPECT" if "inspect" in eng.lower() else "INSPECTED"
            cf = con.split("Stored astrofuel: ")[-1].split("'")[0][:9] if "Stored astrofuel" in con else "?"
            rng = con.split("Gravship range: ")[-1].split("'")[0][:5] if "Gravship range" in con else "?"
            f1 = t1.split("Astrofuel stored: ")[-1].split(" l'")[0][:9] if "Astrofuel stored" in t1 else "?"
            print(f"t+{(i+1)*10}s {ins} console={cf} tank={f1} range={rng}", flush=True)
            if ins == "INSPECTED" and cf[:1] not in "0?":
                print("SHIP READY", flush=True); break
    except Exception as e:
        print("probe:", str(e)[:60], flush=True)
with fresh() as rb:
    rb.call("rimworld/set_time_speed", {"speed": 0})
    print("paused", flush=True)
