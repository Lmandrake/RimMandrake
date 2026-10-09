import sys, json, collections
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
allc = [(x, z) for x in range(1, 100, 3) for z in range(1, 100, 3)]
best = []
for i in range(0, len(allc), 190):
    chunk = ";".join("%d,%d" % c for c in allc[i:i+190])
    for c in S.call("jawa/shadegrid_read", cells=chunk).get("cells") or []:
        if c.get("shade", 0) > 0: best.append((round(c["shade"], 2), c["x"], c["z"]))
best.sort(reverse=True)
print(len(allc), "cells scanned; shaded:", len(best), best[:12])
th = S.call("jawa/list_things", limit=20, rect="0,0,100,100")
print(list(th.keys()))
import collections
t = S.call("jawa/list_things", rect="0,0,100,100", limit=500).get("things") or []
print(collections.Counter(x.get("def") for x in t).most_common(15))
