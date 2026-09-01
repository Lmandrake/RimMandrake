import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    try:
        rb.call("jawa/set_pawn_faction", {"bogus":1})
    except Exception as e:
        print("declared:", str(e).split("Declared:")[-1].strip())
    r = rb.call("jawa/set_pawn_faction", {"pawn": "Thrumbo79608", "faction": "AncientsHostile"})
    print("faction:", r.get("success"), str(r)[:120])
    h0 = rb.call("jawa/pawn_health", {"pawn": "Thrumbo79608"})
    print("health before:", str(h0)[:200])
    rb.call("rimworld/step_game_ticks", {"ticks": 240})
    h1 = rb.call("jawa/pawn_health", {"pawn": "Thrumbo79608"})
    print("after 240:", str(h1)[:400])
    ins = rb.call("jawa/inspect_string", {"thingIds": "Turret_Sniper" })
