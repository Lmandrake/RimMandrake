import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("rimworld/set_time_speed", {"speed": 0})
    t1 = rb.call("rimworld/get_game_info", {}).get("ticksGame")
    time.sleep(3)
    t2 = rb.call("rimworld/get_game_info", {}).get("ticksGame")
    print("paused:", t1 == t2, t1, t2)
    tanks = rb.call("jawa/list_things", {"defName": "ChemfuelTank", "rect": "143,59,86,133", "limit": 5}).get("things", [])
    print("tanks in footprint:", [(t["id"], t["x"], t["z"]) for t in tanks])
    mins = rb.call("jawa/list_things", {"defName": "MinifiedThing", "limit": 10}).get("things", [])
    for m in mins:
        ci = rb.call("rimworld/get_cell_info", {"x": m["x"], "z": m["z"]})
        inner = [t.get("defName") for t in ci.get("things", [])]
        print("minified at", m["x"], m["z"], "->", inner)
