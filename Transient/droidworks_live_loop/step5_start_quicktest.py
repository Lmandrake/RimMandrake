import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

# Step 1: go to main menu (a game/save is currently loaded)
with RimBridge(host, port, token) as rb:
    r = rb.call("rimworld/go_to_main_menu", {})
    print("go_to_main_menu:", r.get("success"), r.get("operation", {}).get("Success"))

time.sleep(3)

# Step 2: start_debug_game_ready. This call itself may exceed the 30s client
# timeout and desync the connection -- per rimbridge skill, do NOT retry on
# the same connection. Open a fresh one and poll list_pawns instead.
try:
    with RimBridge(host, port, token) as rb:
        r = rb.call("rimworld/start_debug_game_ready", {})
        print("start_debug_game_ready (in-time):", r)
except Exception as e:
    print("start_debug_game_ready call desynced/timed out as expected:", repr(e))

# Step 3: poll on a FRESH connection until a map exists
deadline = time.time() + 120
ok = False
while time.time() < deadline:
    time.sleep(5)
    try:
        with RimBridge(host, port, token) as rb:
            r = rb.call("jawa/list_pawns", {})
            msg = r.get("message", "")
            print("poll:", r.get("success"), msg)
            if r.get("success") and "No current map" not in msg:
                ok = True
                break
    except Exception as e:
        print("poll error:", repr(e))

print("READY" if ok else "TIMED OUT WAITING FOR MAP")
