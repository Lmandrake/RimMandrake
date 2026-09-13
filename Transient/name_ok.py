import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("rimworld/click_ui_target", {"targetId": "ui-element:4:6:7"})
    print("OK click:", r.get("success"), str(r.get("message",""))[:60])
    time.sleep(0.5)
    ui = rb.call("rimworld/get_ui_state", {})
    wins = [w if isinstance(w, str) else w.get("type") for w in ui.get("windows", [])]
    print("windows now:", wins)
    rb.call("rimworld/set_time_speed", {"speed": 1})
    t1 = rb.call("rimworld/get_game_info", {}).get("ticksGame")
    time.sleep(4)
    t2 = rb.call("rimworld/get_game_info", {}).get("ticksGame")
    print("ticks:", t1, "->", t2, "| TIME RUNS" if t2 > t1 else "| still stuck")
