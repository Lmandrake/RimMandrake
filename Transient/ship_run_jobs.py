import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    # nudge a colonist to the engine first so inspection is the nearest job
    rb.call("jawa/order_pawn", {"pawnId": "Human922", "targetId": "GravEngine466248", "pathEndMode": "InteractionCell", "unpause": False})
    rb.call("rimworld/set_time_speed", {"speed": 3})
    for i in range(20):
        time.sleep(12)
        r = rb.call("jawa/inspect_string", {"thingIds": "ChemfuelTank466253,GravEngine466248,PilotConsole469283"})
        rows = {x.get("id"): str(x.get("inspect") or x.get("text")) for x in r.get("things", r.get("results", []))}
        tank = rows.get("ChemfuelTank466253","")
        eng = rows.get("GravEngine466248","")
        con = rows.get("PilotConsole469283","")
        fuel = tank.split("Astrofuel stored:")[-1][:12] if "Astrofuel stored" in tank else "?"
        rng = con.split("Gravship range:")[-1][:6] if "Gravship range" in con else "?"
        need_inspect = "inspect" in eng.lower()
        print(f"t+{(i+1)*12}s tank{fuel} range{rng} inspect_needed={need_inspect}", flush=True)
        if not need_inspect and "0 / 250" not in tank:
            print("GATES CLEARING", flush=True)
            break
    rb.call("rimworld/set_time_speed", {"speed": 0})
    print("paused again", flush=True)
