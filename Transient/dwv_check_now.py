import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
try:
    host, port, token = resolve_endpoint()
    with RimBridge(host, port, token) as rb:
        r = rb.call("rimworld/get_ui_state", {})
        print("ui_state:", json.dumps(r)[:400])
except Exception as e:
    print("EXC:", str(e)[:300])
