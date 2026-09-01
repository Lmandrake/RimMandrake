import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ps = rb.call("jawa/list_pawns", {})
    th = [p for p in ps.get("pawns", []) if p.get("id")=="Thrumbo79608"][0]
    print("thrumbo hostile flag:", th.get("hostile"), "| faction:", th.get("faction"))
    r = rb.call("rimworld/execute_debug_action", {"path": "Actions\\Spawn Pawn...\\Megascarab", "x": 300, "z": 40})
    rb.call("rimworld/step_game_ticks", {"ticks": 400})
    ins = rb.call("jawa/inspect_string", {"thingIds": "Turret_Sniper"})
    print("sniper:", str((ins.get("things") or [{}])[0].get("inspect"))[:160])
    ps = rb.call("jawa/list_pawns", {})
    for p in ps.get("pawns", []):
        if "egascarab" in str(p.get("kind")) or p.get("id")=="Thrumbo79608":
            print(p.get("id"), p.get("x"), p.get("z"), "hostile:", p.get("hostile"), "downed:", p.get("downed"))
