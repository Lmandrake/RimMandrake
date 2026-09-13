import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=60.0) as rb:
    r = rb.call("rimworld/save_game", {"saveName": "CANONICAL_ASHKARR_2026-09-09"})
    print(json.dumps(r)[:1500])
