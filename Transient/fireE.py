import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ins = rb.call("jawa/inspect_string", {"defName": "Turret_Sniper"})
    for t in ins.get("things", []):
        print(t.get("id"), t.get("x"), t.get("z"), "|", str(t.get("inspect"))[:140])
    rb.call("rimworld/step_game_ticks", {"ticks": 600})
    ins = rb.call("jawa/inspect_string", {"defName": "Turret_Sniper"})
    for t in ins.get("things", []):
        print("after600:", str(t.get("inspect"))[:140])
    h = rb.call("jawa/pawn_health", {"pawn": "Thrumbo79608", "action": "list"})
    print("thrumbo hediffs:", str(h.get("hediffs"))[:300])
