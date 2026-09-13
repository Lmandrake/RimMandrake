import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
CID = "architect-designator:orders:highlight-designator-tutortagnotset-7"
with RimBridge(host, port, token) as rb:
    d = rb.call("rimworld/apply_architect_designator", {"designatorId": CID, "x": 143, "z": 59, "width": 86, "height": 133, "dryRun": True})
    print("dry:", d.get("success"), str(d.get("message",""))[:150], d.get("applicableCells", d.get("cellCount")))
    if d.get("success"):
        r = rb.call("rimworld/apply_architect_designator", {"designatorId": CID, "x": 143, "z": 59, "width": 86, "height": 133})
        print("apply:", r.get("success"), str(r.get("message",""))[:150])
        rb.call("jawa/map_commit", {})
        for dn in ("GravEngine","SmallThruster","ChemfuelTank","VFE_LargeAdvancedBattery","GravshipHull"):
            chk = rb.call("jawa/list_things", {"defName": dn, "rect": "143,59,86,133", "limit": 2})
            th = chk.get("things", [{}])
            print(dn, "faction:", th[0].get("factionName") if th else "?")
