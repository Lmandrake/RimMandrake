import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    try:
        r = rb.call("rimworld/start_debug_game_ready", {"readiness": "playable", "pauseIfNeeded": True})
        print("start_debug_game_ready:", json.dumps(r)[:800])
    except Exception as e:
        print("start_debug_game_ready EXC (expected timeout maybe):", str(e)[:400])
