import sys, re
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for burst in range(4):
        rb.call("rimworld/step_game_ticks", {"ticks": 1000})
        ins = rb.call("jawa/inspect_string", {"defName": "Turret_Sniper"})
        shots = str((ins.get("things") or [{}])[0].get("inspect"))
        m = re.search(r"rearm: (\d+)", shots)
        ps = rb.call("jawa/list_pawns", {})
        th = [p for p in ps.get("pawns", []) if p.get("id")=="Thrumbo79608"]
        state = {k:th[0].get(k) for k in ('x','z','downed','dead')} if th else "GONE/DEAD"
        print(f"burst {burst}: shots left {m.group(1) if m else '?'} | thrumbo {state}")
        if not th or th[0].get("downed") or th[0].get("dead"): break
    r = rb.call("rimworld/save_game", {"saveName": "qt_fire_probe3"})
    print("saved:", r.get("success"))
