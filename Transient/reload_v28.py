import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("rimworld/load_game", {"saveName": "WORLDMAP_V28_punchlist_2026-09-09"})
    print("queued:", r.get("status"), flush=True)
time.sleep(15)
for i in range(30):
    try:
        with RimBridge(host, port, token) as rb:
            gi = rb.call("rimworld/get_game_info", {})
            t = gi.get("ticksGame")
            if t and t < 100000:
                print(f"V28 restored (ticks {t})", flush=True)
                break
            print(f"poll {i}: ticks {t}", flush=True)
    except Exception as e:
        print(f"poll {i}: quiet", flush=True)
    time.sleep(8)
