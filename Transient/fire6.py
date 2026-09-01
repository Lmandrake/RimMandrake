import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/set_thing_props", {"thing": "BigLaserCannon22478", "faction": "Player"})
    print("faction set:", str(r)[:200])
    r = rb.call("rimworld/step_game_ticks", {"ticks": 400})
    ps = rb.call("jawa/list_pawns", {})
    scar = [p for p in ps.get("pawns", []) if "egascarab" in str(p.get("kind"))]
    print("scarab:", (str(scar[0])[:260] if scar else "GONE - killed"))
    ins = rb.call("jawa/inspect_string", {"thingIds": "BigLaserCannon22478"})
    print("turret:", str((ins.get("things") or [{}])[0].get("inspect"))[:200])
