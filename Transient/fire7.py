import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/set_thing_props", {"thing": "BigLaserCannon22478", "faction": "PlayerColony"})
    print("faction:", r.get("success"), str(r.get("faction") or r)[:120])
    rb.call("rimworld/step_game_ticks", {"ticks": 600})
    ps = rb.call("jawa/list_pawns", {})
    scar = [p for p in ps.get("pawns", []) if "egascarab" in str(p.get("kind"))]
    if scar:
        s = scar[0]
        print("scarab alive | downed:", s.get("downed"), "| hp-ish:", {k: s.get(k) for k in ("health","summaryHealth","downed","dead") if k in s})
    else:
        print("scarab GONE - killed by turret")
    t1 = rb.call("rimworld/get_game_info", {}).get("ticksGame")
    print("ticks now:", t1)
