import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: Destroy", "thingId": "Thing_Megascarab79664"})
    rb.call("rimworld/step_game_ticks", {"ticks": 2000})
    ins = rb.call("jawa/inspect_string", {"defName": "Turret_Sniper"})
    print("sniper:", str((ins.get("things") or [{}])[0].get("inspect"))[:130])
    ps = rb.call("jawa/list_pawns", {})
    th = [p for p in ps.get("pawns", []) if p.get("id")=="Thrumbo79608"]
    print("thrumbo:", (str({k:th[0].get(k) for k in ('x','z','downed','dead')})) if th else "GONE (dead)")
    r = rb.call("rimworld/save_game", {"saveName": "qt_fire_probe2"})
    print("saved:", r.get("success"))
