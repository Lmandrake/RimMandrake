import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    st = rb.call("rimbridge/get_bridge_status", {})
    print("pre-load state:", json.dumps(st.get("state"))[:300])
    r = rb.call("rimworld/load_game", {"saveName": "CANONICAL_ASHKARR_2026-09-09"})
    print("load_game result:", json.dumps(r)[:400])
