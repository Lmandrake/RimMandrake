import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
import game_focus
try:
    game_focus.preflight()
except Exception as e:
    print("preflight:", e)

host, port, token = resolve_endpoint()
try:
    with RimBridge(host, port, token) as rb:
        r = rb.call("rimworld/start_debug_game_ready", {"readiness": "playable", "timeoutMs": 180000, "pauseIfNeeded": True})
        print("START:", json.dumps(r)[:400])
except Exception as e:
    print("start call raised (expected on timeout):", type(e).__name__, e)

# fresh connection, poll
for i in range(40):
    time.sleep(10)
    try:
        host, port, token = resolve_endpoint()
        with RimBridge(host, port, token) as rb:
            r = rb.call("jawa/list_pawns", {"limit": 1})
        s = json.dumps(r)
        if "No current map" in s:
            print(i, "no map yet"); continue
        print(i, "MAP READY:", s[:200]); break
    except Exception as e:
        print(i, "poll err", type(e).__name__, str(e)[:120])
