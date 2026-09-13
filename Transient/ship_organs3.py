import sys
from collections import Counter
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for d in ("GravEngine","GravFieldExtender","GravshipThruster","SmallThruster","LargeThruster","ChemfuelTank","PilotConsole","GravshipHull","Battery"):
        r = rb.call("jawa/list_things", {"defName": d, "rect": "143,59,86,133", "limit": 3000})
        n = r.get("count", len(r.get("things", [])))
        row = r.get("things", [])[:1]
        pos = (row[0].get("x"), row[0].get("z")) if row else None
        fac = row[0].get("factionName") if row else None
        print(f"{d}: {n}  first at {pos} faction={fac}")
