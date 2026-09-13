import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    p = rb.call("jawa/list_pawns", {"faction": "PlayerColony", "limit": 8, "includeHealth": True})
    for c in p.get("pawns", []):
        print(c.get("id"), c.get("name") or "?", "at", c.get("x"), c.get("z"), "| downed:", c.get("downed"), "| mental:", c.get("mentalState"), "| job:", c.get("jobLabel") or c.get("job"))
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions"}).get("children", [])
    comp = [c["path"] for c in ch if "complete" in c["path"].lower() or "maint" in c["path"].lower()]
    print("complete-ish actions:", comp)
