import json, sys, collections
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from kink import kinks, resample
import math
def length(s): return sum(math.hypot(b[0]-a[0], b[1]-a[1]) for a, b in zip(s, s[1:]))
d = json.load(open(sys.argv[1]))
rows = []
for p in d["pieces"]:
    for si, s in enumerate(p["strands"]):
        if len(s) < 3: continue
        L = length(s)
        for arc, x, z, deg in kinks(s):
            near = "A" if arc <= L - arc else "B"
            fe = min(arc, L - arc)
            end = p["a"] if near == "A" else p["b"]
            kind = (end or "pile").split(":")[0] if p["b"] or near == "A" else "pile"
            if p["a"].startswith("tangle:(") : kind = "tanglecable"
            rows.append((kind, round(fe, 2), deg, p["a"], p["b"], si, x, z))
c = collections.Counter(r[0] for r in rows)
print("kinks", len(rows), dict(c))
band = collections.Counter(("<0.25" if r[1] < .25 else "<0.75" if r[1] < .75 else ">=0.75") for r in rows)
print("from-end", dict(band))
for r in sorted(rows)[: int(sys.argv[2]) if len(sys.argv) > 2 else 400]: print(r)
