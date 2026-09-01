import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    try:
        r = rb.call("rimworld/get_bridge_status", {})
        print("status before:", r)
    except Exception as e:
        print("status exception:", e)

with RimBridge(host, port, token) as rb:
    try:
        r = rb.call("rimworld/start_debug_game_ready", {}, timeout=35)
        print("start_debug_game_ready (early return):", r)
    except Exception as e:
        print("start_debug_game_ready exception (expected - late response):", repr(e))
