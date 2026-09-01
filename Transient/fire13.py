import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    c = rb.call("rimworld/spawn_thing", {"defName":"VanometricPowerCell","x":223,"z":33})
    print("cell2:", c.get("thingId"))
    rb.call("rimworld/step_game_ticks", {"ticks": 900})
    zi = rb.call("jawa/inspect_string", {"thingIds": "Turret_Zapper22562"})
    print("zapper:", str((zi.get("things") or [{}])[0])[:200])
    si = rb.call("jawa/inspect_string", {"thingIds": "Turret_Sniper22521"})
    print("sniper:", str((si.get("things") or [{}])[0].get("label")), str((si.get("things") or [{}])[0].get("inspect"))[:150])
    ps = rb.call("jawa/list_pawns", {})
    scars = [(s.get("id"), s.get("x"), s.get("z"), s.get("downed")) for s in ps.get("pawns", []) if "egascarab" in str(s.get("kind"))]
    print("scarabs:", len(scars), scars)
