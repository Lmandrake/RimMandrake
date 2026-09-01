import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("rimworld/step_game_ticks", {"ticks": 400})
    for hd in ("Gunshot",):
        h = rb.call("jawa/pawn_health", {"pawn": "Thrumbo79608", "hediff": hd})
        print(hd, ":", str(h)[:400])
    ins = rb.call("jawa/inspect_string", {"thingIds": "Thrumbo79608"})
    print("inspect:", str((ins.get("things") or [{}])[0])[:280])
    si = rb.call("jawa/inspect_string", {"thingIds": "Turret_Sniper"})
    ps = rb.call("jawa/list_pawns", {})
    th = [p for p in ps.get("pawns", []) if "hrumbo" in str(p.get("kind"))]
    print("alive:", bool(th), th[0].get("downed") if th else "", th[0].get("x") if th else "", th[0].get("z") if th else "")
