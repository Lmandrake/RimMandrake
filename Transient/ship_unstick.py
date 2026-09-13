import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions"}).get("children", [])
    unforbid = [c["path"] for c in ch if "forbid" in c["path"].lower()]
    print("forbid actions:", unforbid)
    fuel = rb.call("jawa/list_things", {"defName": "VGE_Astrofuel", "rect": "143,59,86,133", "limit": 10}).get("things", [])
    print("fuel stacks:", [(t["id"], t.get("stackCount")) for t in fuel])
    for p in (unforbid or []):
        if "un" in p.lower():
            for t in fuel:
                r = rb.call("rimworld/execute_debug_action", {"path": p, "thingId": "Thing_" + t["id"]})
            print("unforbade via", p)
            break
    # engine inspect gizmo
    rb.call("rimworld/click_cell", {"x": 187, "z": 150})
    time.sleep(0.3)
    g = rb.call("rimworld/list_selected_gizmos", {})
    labels = [(z.get("label"), str(z.get("gizmoId"))[:50]) for z in g.get("gizmos", [])]
    print("engine gizmos:", labels)
