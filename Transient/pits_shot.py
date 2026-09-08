import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=20) as rb:
    rb.call("jawa/clear_ui", {})
    r = rb.call("rimworld/take_screenshot", {"fileName": "pits_oiled_ignite_fixed_2026-09-06"})
    print(json.dumps(r)[:400])
