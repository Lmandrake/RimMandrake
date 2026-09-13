import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
CID = "architect-designator:orders:highlight-designator-tutortagnotset-7"
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/list_things", {"group": "building", "rect": "143,59,86,133", "limit": 8000})
    things = r.get("things", [])
    unclaimed_cells = sorted({(t["x"], t["z"]) for t in things if not t.get("factionName")})
    print("buildings:", len(things), "| unclaimed cells:", len(unclaimed_cells))
    # test one
    x, z = unclaimed_cells[0]
    t1 = rb.call("rimworld/apply_architect_designator", {"designatorId": CID, "x": x, "z": z, "width": 1, "height": 1})
    print("test cell:", t1.get("success"), str(t1.get("message",""))[:100])
    if t1.get("success"):
        n = 0
        for x, z in unclaimed_cells[1:]:
            rr = rb.call("rimworld/apply_architect_designator", {"designatorId": CID, "x": x, "z": z, "width": 1, "height": 1, "keepSelected": True})
            n += 1 if rr.get("success") else 0
        print("claimed cells:", n+1, "of", len(unclaimed_cells))
        rb.call("jawa/map_commit", {})
        for dn in ("GravEngine","SmallThruster","ChemfuelTank","VFE_LargeAdvancedBattery","GravshipHull","GravFieldExtender"):
            chk = rb.call("jawa/list_things", {"defName": dn, "rect": "143,59,86,133", "limit": 2})
            th = chk.get("things", [{}])
            print(dn, "faction:", th[0].get("factionName") if th else "?")
