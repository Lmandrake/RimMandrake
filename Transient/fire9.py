import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    t = rb.call("rimworld/spawn_thing", {"defName":"Turret_Sniper","x":230,"z":23})
    tid = t.get("thingId"); print("sniper:", tid, t.get("label"))
    bare = tid.replace("Thing_","")
    r = rb.call("jawa/set_thing_props", {"thing": bare, "faction": "PlayerColony"})
    print("faction:", r.get("success"))
    ins = rb.call("jawa/inspect_string", {"thingIds": bare})
    print("inspect:", str((ins.get("things") or [{}])[0].get("inspect"))[:250])
    rb.call("rimworld/step_game_ticks", {"ticks": 700})
    ps = rb.call("jawa/list_pawns", {})
    scar = [p for p in ps.get("pawns", []) if "egascarab" in str(p.get("kind"))]
    print("scarab:", ("ALIVE downed=%s" % scar[0].get("downed")) if scar else "GONE - killed")
