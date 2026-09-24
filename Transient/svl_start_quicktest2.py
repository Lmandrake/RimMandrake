import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
try:
    with RimBridge(host, port, token) as rb:
        r = rb.call("rimworld/start_debug_game_ready", {})
        print("START_RESULT", json.dumps(r)[:800])
except Exception as e:
    print("START_CALL_EXCEPTION (expected if it times out per skill)", repr(e))
