import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions"}).get("children", [])
    claims = [c["path"] for c in ch if "claim" in c["path"].lower()]
    print("claim actions:", claims)
    if claims:
        P = claims[0]
        e = rb.call("jawa/list_things", {"defName": "GravEngine", "rect": "143,59,86,133", "limit": 2})
        tid = e["things"][0]["id"]
        print("engine id:", tid)
        r = rb.call("rimworld/execute_debug_action", {"path": P, "thingId": f"Thing_{tid}" if not str(tid).startswith("Thing") else tid})
        print("claim engine:", r.get("success"), r.get("message",""))
        chk = rb.call("jawa/list_things", {"defName": "GravEngine", "rect": "143,59,86,133", "limit": 2})
        print("engine faction now:", chk["things"][0].get("factionName"))
