import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("rimworld/step_game_ticks", {"ticks": 1500})
    h = rb.call("jawa/pawn_health", {"pawn": "Thrumbo79608", "action": "list"})
    print("thrumbo:", json.dumps(h)[:500])
    ps = rb.call("jawa/list_pawns", {})
    for p in ps.get("pawns", []):
        if p.get("id") in ("Thrumbo79608","Megascarab79664"):
            print(p.get("id"), "at", p.get("x"), p.get("z"), "downed:", p.get("downed"), "dead:", p.get("dead"))
    ins = rb.call("jawa/inspect_string", {"defName": "Turret_Sniper"})
    print("sniper:", str((ins.get("things") or [{}])[0].get("inspect"))[:120])
