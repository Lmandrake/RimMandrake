import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for did in ("Claim", "Designator_Claim", "Orders/Claim"):
        r = rb.call("rimworld/apply_architect_designator", {"designatorId": did, "x": 143, "z": 59, "width": 86, "height": 133, "dryRun": True})
        print(did, "->", r.get("success"), str(r.get("message",""))[:120], r.get("affectedCells", r.get("cells")))
        if r.get("success"): break
