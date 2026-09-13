import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/designate_batch", {"designator": "Claim", "rect": "143,59,86,133"})
    print("claim:", r.get("success"), r.get("designated", r.get("message","?")))
    rb.call("jawa/map_commit", {})
    chk = rb.call("jawa/list_things", {"defName": "GravEngine", "rect": "143,59,86,133", "limit": 2})
    print("engine faction now:", chk.get("things",[{}])[0].get("factionName"))
