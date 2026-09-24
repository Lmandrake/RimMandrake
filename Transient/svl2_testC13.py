import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/select_things", {"ids": "RSW_BactaTank692523", "action": "select"})
    print("SELECT", json.dumps(r)[:800])
    g = rb.call("rimworld/list_selected_gizmos", {})
    print("GIZMOS_COUNT", g.get("gizmoCount"))
    for gz in g.get("gizmos", []):
        print("  ", gz.get("label"), "|", gz.get("defaultDesc", "")[:80])
