import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
print("endpoint", host, port)
with RimBridge(host, port, token) as rb:
    res = rb.call("rimworld/load_game_ready", {"saveName": "CANONICAL_ASHKARR_2026-09-09"})
    print(json.dumps(res, indent=2)[:4000])
