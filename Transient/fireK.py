import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions\\Mental state..."})["children"]
    mh = [c["path"] for c in ch if "anhunter" in c["path"]]
    print("leaves:", mh[:3])
    if mh:
        r = rb.call("rimworld/execute_debug_action", {"path": mh[0], "x": 299, "z": 62})
        print("manhunter:", r.get("success"), str(r.get("effects") or "")[:100])
    rb.call("rimworld/step_game_ticks", {"ticks": 1200})
    ins = rb.call("jawa/inspect_string", {"defName": "Turret_Sniper"})
    print("sniper:", str((ins.get("things") or [{}])[0].get("inspect"))[:130])
    ps = rb.call("jawa/list_pawns", {})
    th = [p for p in ps.get("pawns", []) if p.get("id")=="Thrumbo79608"]
    print("thrumbo:", (str({k:th[0].get(k) for k in ('x','z','downed','dead')})) if th else "GONE")
