import sys, json, os, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
try:
    with RimBridge(host, port, token) as rb:
        r = rb.call("rimworld/start_debug_game_ready", {"readiness":"currentMap","timeoutMs":180000,"pauseIfNeeded":True})
        print("start:", json.dumps(r)[:400])
except Exception as e:
    print("start raised (expected if late):", type(e).__name__, str(e)[:200])
for i in range(20):
    time.sleep(10)
    try:
        with RimBridge(host, port, token) as rb:
            g = rb.call("rimworld/get_game_info", {})
            print("poll", i, json.dumps(g)[:500])
            if g.get("success"):
                break
    except Exception as e:
        print("poll", i, "err", str(e)[:120])
