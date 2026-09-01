import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ps = rb.call("jawa/list_pawns", {})
    th = [p for p in ps.get("pawns", []) if p.get("id")=="Thrumbo79608"][0]
    tx, tz = th["x"], th["z"]
    print("thrumbo at", tx, tz)
    # pad in its neighborhood
    px, pz = tx+8, tz
    rb.call("jawa/destroy_batch", {"rects": f"{px-6},{pz-6},{px+6},{pz+6}", "categories": "Plant"})
    c = rb.call("rimworld/spawn_thing", {"defName":"VanometricPowerCell","x":px,"z":pz})
    ids = {}
    for dn,(dx,dz) in {"Turret_Zapper":(2,2),"VFES_Turret_TeslaBlaster":(2,-2),"VFES_Turret_Flame":(-2,2)}.items():
        t = rb.call("rimworld/spawn_thing", {"defName":dn,"x":px+dx,"z":pz+dz})
        tid = t["thingId"].replace("Thing_","")
        rb.call("jawa/set_thing_props", {"thing": tid, "faction": "PlayerColony"})
        ids[dn]=tid
    print("pad up:", ids)
    for i in range(3):
        rb.call("rimworld/step_game_ticks", {"ticks": 800})
        ps = rb.call("jawa/list_pawns", {})
        th = [p for p in ps.get("pawns", []) if p.get("id")=="Thrumbo79608"]
        st = {k:th[0].get(k) for k in ('x','z','downed','dead')} if th else "GONE/DEAD"
        print("step", i, st)
        if not th or th[0].get("dead") or th[0].get("downed"): break
    r = rb.call("rimworld/save_game", {"saveName": "qt_fire_probe4"})
    print("saved:", r.get("success"))
