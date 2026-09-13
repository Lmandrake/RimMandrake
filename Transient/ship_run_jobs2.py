import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def fresh(): return RimBridge(host, port, token)
with fresh() as rb:
    rb.call("rimworld/set_time_speed", {"speed": 3})
for i in range(22):
    time.sleep(12)
    try:
        with fresh() as rb:
            r = rb.call("jawa/inspect_string", {"thingIds": "ChemfuelTank466253,ChemfuelTank466254,GravEngine466248,PilotConsole469283"})
            rows = {x.get("id"): str(x.get("inspect") or x.get("text")) for x in r.get("things", r.get("results", []))}
            t1 = rows.get("ChemfuelTank466253",""); t2 = rows.get("ChemfuelTank466254","")
            eng = rows.get("GravEngine466248",""); con = rows.get("PilotConsole469283","")
            f1 = t1.split("Astrofuel stored: ")[-1].split(" l'")[0][:10] if "Astrofuel stored" in t1 else "?"
            f2 = t2.split("Astrofuel stored: ")[-1].split(" l'")[0][:10] if "Astrofuel stored" in t2 else "?"
            rng = con.split("Gravship range: ")[-1].split("'")[0][:5] if "Gravship range" in con else "?"
            cf = con.split("Stored astrofuel: ")[-1].split("'")[0][:10] if "Stored astrofuel" in con else "?"
            ins = "NEEDS-INSPECT" if "inspect" in eng.lower() else "inspected"
            g = rb.call("rimworld/get_game_info", {})
            print(f"t+{(i+1)*12}s ticks={g.get('ticksGame')} tank1={f1} tank2={f2} console={cf} range={rng} {ins}", flush=True)
            if ins == "inspected" and ("0 /" not in cf or f1[:1] not in "0?"):
                print("GATES CLEARED", flush=True)
                break
    except Exception as e:
        print(f"t+{(i+1)*12}s probe: {str(e)[:50]}", flush=True)
with fresh() as rb:
    rb.call("rimworld/set_time_speed", {"speed": 0})
    print("paused", flush=True)
