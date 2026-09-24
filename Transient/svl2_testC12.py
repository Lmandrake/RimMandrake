import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("rimworld/click_cell", {"x": 171, "z": 139})
    print("CLICK", json.dumps(r)[:600])
    g = rb.call("rimworld/list_selected_gizmos", {})
    print("GIZMOS", json.dumps(g)[:3000])
