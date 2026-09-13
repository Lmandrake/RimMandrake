import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/designate_batch", {"designation": "Claim", "rect": "143,59,86,133", "onThings": True, "limit": 5000})
    print("claim:", r.get("success"), {k: r.get(k) for k in ("designated","applied","count","message")})
    rb.call("jawa/map_commit", {})
    for d in ("GravEngine","SmallThruster","ChemfuelTank","VFE_LargeAdvancedBattery","GravFieldExtender"):
        chk = rb.call("jawa/list_things", {"defName": d, "rect": "143,59,86,133", "limit": 2})
        th = chk.get("things", [{}])
        print(d, "faction:", th[0].get("factionName") if th else "none-found")
