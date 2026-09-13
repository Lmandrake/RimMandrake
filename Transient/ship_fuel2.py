import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions"}).get("children", [])
    hits = [c["path"] for c in ch if any(s in c["path"].lower() for s in ("refuel","astro","chem","t: fill","set fuel"))]
    print("hits:", hits)
    more = [c["path"] for c in ch if "more" in c["path"].lower()]
    print("more nodes:", more)
    if more:
        ch2 = rb.call("rimworld/list_debug_action_children", {"path": more[0]}).get("children", [])
        hits2 = [c["path"] for c in ch2 if any(s in c["path"].lower() for s in ("refuel","fuel"))]
        print("under more:", hits2[:6])
