import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ui = rb.call("rimworld/get_ui_state", {})
    print("UI_STATE", json.dumps(ui)[:2000])
    stats = rb.call("jawa/world_stats", {})
    print("WORLD_STATS", json.dumps(stats)[:4000])
