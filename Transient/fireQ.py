import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    c = rb.call("rimworld/spawn_thing", {"defName":"VanometricPowerCell","x":298,"z":28})
    b = rb.call("rimworld/spawn_thing", {"defName":"VFES_Turret_Ballista","x":300,"z":30})
    bid = b["thingId"].replace("Thing_","")
    rb.call("jawa/set_thing_props", {"thing": bid, "faction": "PlayerColony"})
    s = rb.call("rimworld/select_pawn", {"pawnId": "Thing_Thrumbo79608"})
    print("select:", s.get("success"), str(s.get("message") or "")[:60])
    t = rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: Teleport", "x": 300, "z": 38})
    print("teleport:", t.get("success"))
    ps = rb.call("jawa/list_pawns", {})
    th = [p for p in ps.get("pawns", []) if p.get("id")=="Thrumbo79608"][0]
    print("thrumbo now:", th["x"], th["z"])
    for i in range(3):
        rb.call("rimworld/step_game_ticks", {"ticks": 350})
        ps = rb.call("jawa/list_pawns", {})
        th = [p for p in ps.get("pawns", []) if p.get("id")=="Thrumbo79608"]
        st = {k:th[0].get(k) for k in ('x','z','downed','dead')} if th else "GONE/DEAD"
        ins = rb.call("jawa/inspect_string", {"thingIds": bid})
        bolts = str((ins.get("things") or [{}])[0].get("inspect"))
        print(i, st, "|", bolts[:60])
        if not th or th[0].get("downed") or th[0].get("dead"): break
    rb.call("rimworld/save_game", {"saveName": "qt_fire_probe5"})
