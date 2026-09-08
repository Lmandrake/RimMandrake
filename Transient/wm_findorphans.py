import sys, json, csv
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
mine=set()
for l in csv.DictReader(open(r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_links.csv")):
    if l['kind']=='river': mine.add(frozenset((int(l['a']),int(l['b']))))
myTiles={t for e in mine for t in e}
print("our river links:", len(mine), " our river tiles:", len(myTiles))
h,p,t = resolve_endpoint()
liveLinks=set(); liveTiles=set()
with RimBridge(h,p,t) as rb:
    N=21872; step=90
    for s in range(0, N, step):
        ids=",".join(str(i) for i in range(s, min(s+step, N)))
        try:
            r = rb.call("jawa/world_links_get", {"tiles": ids, "onlyLinked": True, "limit": 100})
        except Exception as e:
            print("chunk", s, "failed:", str(e)[:100]); continue
        for tl in r.get("tiles", []):
            pr = tl.get("potentialRivers") or []
            if pr:
                a=tl.get("tile"); liveTiles.add(a)
                for x in pr: liveLinks.add(frozenset((a, x.get("neighbor"))))
print("live river links:", len(liveLinks), " live river tiles:", len(liveTiles))
extra = liveLinks - mine
xt = sorted(liveTiles - myTiles)
print("ORPHAN links:", len(extra))
print("tiles not in our CSV:", len(xt), xt[:40])
json.dump({"links":[sorted(e) for e in extra], "tiles":xt},
          open(r"D:\Luke\dev\Rimworld\Transient\orphan_rivers.json","w"))
