import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    try:
        r = rb.call("rimworld/load_game", {"saveName": "CANONICAL_ASHKARR_2026-09-09"})
        print("load_game:", json.dumps(r)[:1200])
    except Exception as e:
        print("load_game EXC (may be timeout, expected):", str(e)[:400])
