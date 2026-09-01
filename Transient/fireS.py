import sys, re
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ins = rb.call("jawa/inspect_string", {"defName": "VFES_Turret_Ballista"})
    old = (ins.get("things") or [{}])[0].get("id")
    if old: rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: Destroy", "thingId": "Thing_"+old})
    b = rb.call("rimworld/spawn_thing", {"defName":"VFES_Turret_Ballista","x":310,"z":44})
    bid = b["thingId"].replace("Thing_","")
    rb.call("jawa/set_thing_props", {"thing": bid, "faction": "PlayerColony"})
    ins = rb.call("jawa/inspect_string", {"thingIds": bid})
    print("ballista:", (ins.get("things") or [{}])[0].get("inspect"))
    for i in range(4):
        rb.call("rimworld/step_game_ticks", {"ticks": 400})
        ins = rb.call("jawa/inspect_string", {"thingIds": bid})
        line = str((ins.get("things") or [{}])[0].get("inspect"))
        ps = rb.call("jawa/list_pawns", {})
        th = [p for p in ps.get("pawns", []) if p.get("id")=="Thrumbo79608"]
        st = {k:th[0].get(k) for k in ('x','z','downed','dead')} if th else "GONE/DEAD"
        print(i, st, "|", line[:80])
        m = re.search(r"bolts: (\d)", line)
        if (m and m.group(1) != "4") or not th or th[0].get("downed"): break
    rb.call("rimworld/save_game", {"saveName": "qt_fire_probe6"})
