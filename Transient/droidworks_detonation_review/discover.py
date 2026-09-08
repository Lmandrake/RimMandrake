import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    print("bridge status ok")
    try:
        r = rb.call("rimworld/start_debug_game_ready", {})
        print("start_debug_game_ready:", json.dumps(r)[:300])
    except Exception as e:
        print("start_debug_game_ready EXC (maybe late-timeout, expected):", e)
