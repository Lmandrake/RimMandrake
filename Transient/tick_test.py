import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def fresh(): return RimBridge(host, port, token)
with fresh() as rb:
    rb.call("rimworld/set_time_speed", {"speed": 1})
    t1 = rb.call("rimworld/get_game_info", {}).get("ticksGame")
time.sleep(5)
with fresh() as rb:
    t2 = rb.call("rimworld/get_game_info", {}).get("ticksGame")
    ui = rb.call("rimworld/get_ui_state", {})
    wins = [w if isinstance(w, str) else w.get("type") for w in ui.get("windows", [])]
    print("ticks:", t1, "->", t2, "| advanced:", (t2 or 0) - (t1 or 0))
    print("windows:", wins[:8])
