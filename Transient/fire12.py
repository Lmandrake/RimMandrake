import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/thing_stats", {"thingIds": "Turret_Sniper22521,BigLaserCannon22478"}) if False else None
    ins = rb.call("jawa/inspect_string", {"thingIds": "Turret_Sniper22521"})
    th = (ins.get("things") or [{}])[0]
    print("sniper:", str(th)[:260])
    z = rb.call("rimworld/spawn_thing", {"defName":"Turret_Zapper","x":224,"z":34})
    zid = (z.get("thingId") or "").replace("Thing_",""); print("zapper:", zid, "|", z.get("label"))
    print("faction:", rb.call("jawa/set_thing_props", {"thing": zid, "faction": "PlayerColony"}).get("success"))
    zi = rb.call("jawa/inspect_string", {"thingIds": zid})
    print("zapper inspect:", str((zi.get("things") or [{}])[0].get("inspect"))[:200])
    rb.call("rimworld/step_game_ticks", {"ticks": 500})
    ps = rb.call("jawa/list_pawns", {})
    scars = [(s.get("id"), s.get("x"), s.get("z")) for s in ps.get("pawns", []) if "egascarab" in str(s.get("kind"))]
    print("scarabs:", len(scars), scars)
