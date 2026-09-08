import sys, json, csv
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
mine=set()
for l in csv.DictReader(open(r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_links.csv")):
    if l['kind']=='river': mine.add(frozenset((int(l['a']),int(l['b']))))
print("river links in our CSV:", len(mine))
h,p,t = resolve_endpoint()
live=set()
with RimBridge(h,p,t) as rb:
    r = rb.call("jawa/world_links_get", {"onlyLinked": True, "limit": 2000})
    for tl in r.get("tiles", []):
        a=tl.get("tile")
        for pr in (tl.get("potentialRivers") or []):
            live.add(frozenset((a, pr.get("neighbor"))))
print("river links live      :", len(live))
extra = live - mine
missing = mine - live
print("LIVE-ONLY (orphans to clear):", len(extra))
print("CSV-ONLY (failed to lay)   :", len(missing))
tiles=sorted({t for e in extra for t in e})
print("tiles involved in orphans:", len(tiles))
print("first 30:", tiles[:30])
open(r"D:\Luke\dev\Rimworld\Transient\orphan_river_links.json","w").write(
    json.dumps([sorted(e) for e in extra]))
