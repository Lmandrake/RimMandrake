import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
prev_ticks = 773220
for attempt in range(24):
    time.sleep(10)
    try:
        with RimBridge(host, port, token) as rb:
            ui = rb.call("rimworld/get_ui_state", {})
            st = ui.get("programState")
            try:
                gi = rb.call("rimworld/get_game_info", {})
                ticks = gi.get("ticksGame")
            except Exception:
                ticks = None
            print(f"t+{(attempt+1)*10}s state={st} ticks={ticks}", flush=True)
            if st == "Playing" and ticks is not None and ticks != prev_ticks:
                print("LOADED: new game content answering, ticks differ from gravship save")
                break
    except Exception as e:
        print(f"t+{(attempt+1)*10}s conn: {type(e).__name__}", flush=True)
