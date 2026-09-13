import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("rimworld/list_debug_action_roots", {})
    for root in r.get("roots", []):
        print("ROOT:", root.get("path"), "| tab:", root.get("tabTitle"))
    for path in [x.get("path") for x in r.get("roots", [])]:
        try:
            ch = rb.call("rimworld/list_debug_action_children", {"path": path}).get("children", [])
            hits = [c["path"] for c in ch if any(s in c["path"].lower() for s in ("fuel","refuel"))]
            if hits: print(path, "->", hits)
        except Exception as e:
            print(path, "ERR", str(e)[:40])
