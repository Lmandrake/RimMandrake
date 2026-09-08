import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    try:
        r = rb.call("rimworld/start_debug_game_ready", {})
        print("START:", json.dumps(r)[:800])
    except Exception as e:
        print("START call raised (may be late-timeout, expected):", str(e)[:300])
