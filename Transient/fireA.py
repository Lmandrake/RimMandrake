import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    names = [t["name"] for t in rb.list_tools()]
    print([n for n in names if "health" in n or "hediff" in n or "battle" in n][:8])
    r = rb.call("jawa/destroy_batch", {"rects": "288,6,322,46", "categories": "Plant"})
    print("clear:", r.get("destroyed"))
    c = rb.call("rimworld/spawn_thing", {"defName":"VanometricPowerCell","x":296,"z":18})
    t = rb.call("rimworld/spawn_thing", {"defName":"Turret_Sniper","x":300,"z":22})
    tid = t["thingId"].replace("Thing_","")
    rb.call("jawa/set_thing_props", {"thing": tid, "faction": "PlayerColony"})
    ins = rb.call("jawa/inspect_string", {"thingIds": tid})
    print("sniper:", str((ins.get("things") or [{}])[0].get("inspect"))[:150])
    r = rb.call("rimworld/execute_debug_action", {"path": "Actions\\Spawn Pawn...\\Thrumbo", "x": 300, "z": 41})
    print("thrumbo spawn:", r.get("success"))
    ps = rb.call("jawa/list_pawns", {})
    th = [p for p in ps.get("pawns", []) if "hrumbo" in str(p.get("kind"))]
    print("thrumbo:", str(th[0])[:160] if th else "NOT FOUND")
