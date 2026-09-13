import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
try:
    host, port, token = resolve_endpoint()
    print("endpoint:", host, port, token[:8])
    with RimBridge(host, port, token) as rb:
        r = rb.call("rimworld/get_game_info", {})
        print("game_info:", json.dumps(r)[:500])
except Exception as e:
    print("EXC:", type(e).__name__, str(e)[:300])
