import sys, re
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ps = rb.call("jawa/list_pawns", {})
    th = [p for p in ps.get("pawns", []) if p.get("id")=="Thrumbo79608"][0]
    cx, cz = th["x"], th["z"]; print("pen center:", cx, cz)
    ops = []
    for dx in range(-2,3):
        for dz in range(-2,3):
            if abs(dx)==2 or abs(dz)==2:
                ops.append(f"Fence:{cx+dx},{cz+dz}")
    r = rb.call("jawa/build_batch", {"ops": ";".join(ops), "stuff": "Steel", "faction": "player"})
    print("fences survived:", r.get("survived"), "failed:", len(r.get("failed") or []))
    rb.call("jawa/map_commit", {}) if "jawa/map_commit" in [t["name"] for t in rb.list_tools()] else None
    c = rb.call("rimworld/spawn_thing", {"defName":"VanometricPowerCell","x":cx+12,"z":cz})
    t = rb.call("rimworld/spawn_thing", {"defName":"Turret_Sniper","x":cx+14,"z":cz})
    tid = t["thingId"].replace("Thing_","")
    rb.call("jawa/set_thing_props", {"thing": tid, "faction": "PlayerColony"})
    for i in range(5):
        rb.call("rimworld/step_game_ticks", {"ticks": 400})
        ins = rb.call("jawa/inspect_string", {"thingIds": tid})
        line = str((ins.get("things") or [{}])[0].get("inspect"))
        m = re.search(r"rearm: (\d+)", line)
        ps = rb.call("jawa/list_pawns", {})
        th2 = [p for p in ps.get("pawns", []) if p.get("id")=="Thrumbo79608"]
        st = {k:th2[0].get(k) for k in ('x','z','downed','dead')} if th2 else "GONE/DEAD"
        print(i, "shots left:", m.group(1) if m else "?", "|", st)
        if not th2 or th2[0].get("downed") or th2[0].get("dead"): break
    rb.call("rimworld/save_game", {"saveName": "qt_fire_probe7"})
