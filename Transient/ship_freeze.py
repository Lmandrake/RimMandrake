import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("rimworld/set_time_speed", {"speed": 0})
    t1 = rb.call("rimworld/get_game_info", {}).get("ticksGame")
    time.sleep(4)
    t2 = rb.call("rimworld/get_game_info", {}).get("ticksGame")
    print("ticks stable:", t1, t2, "PAUSED" if t1 == t2 else "STILL RUNNING")
    # the hostile
    h = rb.call("jawa/list_pawns", {"limit": 100})
    for x in h.get("pawns", []):
        if x.get("hostile"):
            r = rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: Destroy", "thingId": "Thing_" + x["id"]})
            print("destroyed hostile", x["id"], "->", r.get("success"))
    # ship damage sample: hull integrity
    hull = rb.call("jawa/list_things", {"defName": "GravshipHull", "rect": "143,59,86,133", "limit": 700}).get("things", [])
    dmg = [t for t in hull if t.get("hitPoints", 0) < t.get("maxHitPoints", 1)]
    print("hull:", len(hull), "damaged:", len(dmg))
    organs = rb.call("jawa/inspect_string", {"thingIds": "GravEngine466248,PilotConsole469283"})
    for row in organs.get("things", organs.get("results", [])):
        print(row.get("id"), str(row.get("inspect") or row.get("text"))[:150])
