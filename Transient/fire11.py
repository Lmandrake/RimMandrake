import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    t = rb.call("rimworld/spawn_thing", {"defName":"VFES_Turret_Ballista","x":238,"z":28})
    tid = (t.get("thingId") or "").replace("Thing_",""); print("ballista:", tid, "|", t.get("label"))
    print("faction:", rb.call("jawa/set_thing_props", {"thing": tid, "faction": "PlayerColony"}).get("success"))
    ins = rb.call("jawa/inspect_string", {"thingIds": tid})
    print("inspect:", str((ins.get("things") or [{}])[0].get("inspect"))[:200])
    rb.call("rimworld/execute_debug_action", {"path": "Actions\\Spawn Pawn...\\Megascarab", "x": 238, "z": 38})
    rb.call("rimworld/step_game_ticks", {"ticks": 800})
    ps = rb.call("jawa/list_pawns", {})
    scars = [p for p in ps.get("pawns", []) if "egascarab" in str(p.get("kind"))]
    print("scarabs alive:", len(scars), [ (s.get("id"), s.get("x"), s.get("z"), s.get("downed")) for s in scars ])
