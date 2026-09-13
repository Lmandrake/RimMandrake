import sys, time
from collections import Counter
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
CID = "architect-designator:orders:highlight-designator-tutortagnotset-7"
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/list_things", {"rect": "143,59,86,133", "limit": 9000})
    things = r.get("things", [])
    fc = Counter(t.get("faction") for t in things)
    print("faction census in footprint:", dict(fc), "| scanned:", r.get("scanned"), "complete:", r.get("isCompleteList"))
    unclaimed = [t for t in things if t.get("faction") is None and t.get("def") not in ("Filth_RubbleRock",) and not str(t.get("def","")).startswith(("Chunk","Rock","Plant"))]
    cells = sorted({(t["x"], t["z"]) for t in unclaimed})
    print("unclaimed non-debris things:", len(unclaimed), "on", len(cells), "cells")
    print("sample defs:", Counter(t["def"] for t in unclaimed).most_common(8))
