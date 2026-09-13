import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions"}).get("children", [])
    fuel = [c["path"] for c in ch if "fuel" in c["path"].lower()]
    print("fuel actions:", fuel)
    tanks = rb.call("jawa/list_things", {"defName": "ChemfuelTank", "rect": "143,59,86,133", "limit": 5}).get("things", [])
    print("tanks:", [(t["id"], t["x"], t["z"]) for t in tanks])
