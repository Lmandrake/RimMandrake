import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
print("endpoint", host, port, token[:8])

# Step 1: go to main menu, then request a fresh debug map. This call is known
# to exceed the 30s client timeout and succeed late -- do not retry it.
with RimBridge(host, port, token) as rb:
    st = rb.call("rimbridge/get_bridge_status", {})
    print("status", json.dumps(st)[:300])
    rb.call("rimworld/go_to_main_menu", {})
    time.sleep(3)
    print("requesting start_debug_game_ready (expect possible timeout)...")
    try:
        r = rb.call("rimworld/start_debug_game_ready", {})
        print("start result", json.dumps(r)[:300])
    except Exception as e:
        print("start_debug_game_ready call ended with:", repr(e)[:200])

print("--- opening FRESH connection to poll for map readiness ---")
deadline = time.time() + 120
map_ready = False
while time.time() < deadline:
    try:
        with RimBridge(host, port, token) as rb2:
            resp = rb2.call("jawa/list_pawns", {})
            text = json.dumps(resp)
            if "No current map" in text:
                print("poll: no current map yet")
            else:
                print("poll: map ready. sample:", text[:300])
                map_ready = True
                break
    except Exception as e:
        print("poll exception:", repr(e)[:200])
    time.sleep(5)

print("MAP_READY" if map_ready else "MAP_NOT_READY_TIMEOUT")
