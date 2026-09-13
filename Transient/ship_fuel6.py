import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for attempt in range(4):
        rb.call("rimworld/click_cell", {"x": 149, "z": 148})
        time.sleep(0.3)
        g = rb.call("rimworld/list_selected_gizmos", {})
        labels = [z.get("label") for z in g.get("gizmos", [])]
        sel = g.get("selected") or g.get("selection")
        print(attempt, "sel:", sel, "gizmos:", labels[:8])
        if any(l and ("fill" in l.lower() or "fuel" in l.lower()) for l in labels if l):
            fz = next(z for z in g.get("gizmos", []) if z.get("label") and ("fill" in z["label"].lower() or "fuel" in z["label"].lower()))
            r = rb.call("rimworld/execute_gizmo", {"gizmoId": fz["gizmoId"]})
            print("fill:", r.get("success"))
            break
