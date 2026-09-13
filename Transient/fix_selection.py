import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("rimworld/clear_selection", {})
    j = rb.call("rimworld/jump_camera_to_cell", {"x": 149, "z": 148})
    print("camera:", j.get("success"))
    time.sleep(0.6)
    c = rb.call("rimworld/click_cell", {"x": 149, "z": 148})
    print("click:", c.get("success"), str(c.get("message",""))[:80])
    time.sleep(0.4)
    g = rb.call("rimworld/list_selected_gizmos", {})
    print("gizmos:", [(z.get("label"), (z.get("gizmoId") or "")[:40]) for z in g.get("gizmos", [])][:12])
    s = rb.call("rimworld/get_selection_semantics", {})
    print("selection:", str(s)[:200])
