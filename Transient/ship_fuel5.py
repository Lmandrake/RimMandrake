import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("rimworld/click_cell", {"x": 149, "z": 148})
    g = rb.call("rimworld/list_selected_gizmos", {})
    for z in g.get("gizmos", []):
        print("-", z.get("label"), "|", str(z.get("gizmoId"))[:60])
