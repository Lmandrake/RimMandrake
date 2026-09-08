import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

# settle window
time.sleep(40)

try:
    with RimBridge(host, port, token) as rb:
        r = rb.call("rimworld/start_debug_game_ready", {})
        print("start_debug_game_ready:", r)
except Exception as e:
    print("start EXC (expected if it exceeds client timeout):", repr(e))

deadline = time.time() + 150
ready = False
while time.time() < deadline:
    try:
        with RimBridge(host, port, token) as rb:
            r = rb.call("jawa/list_pawns", {})
            if r.get("success") and "No current map" not in str(r.get("message", "")):
                print("READY:", r.get("success"))
                ready = True
                break
            else:
                print("waiting:", r.get("message"))
    except Exception as e:
        print("poll exc:", repr(e))
    time.sleep(5)

print("READY_FLAG=" + str(ready))
