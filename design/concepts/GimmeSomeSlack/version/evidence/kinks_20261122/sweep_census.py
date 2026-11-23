import json, sys, os, glob, collections, math
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from kink import kinks
def length(s): return sum(math.hypot(b[0]-a[0], b[1]-a[1]) for a, b in zip(s, s[1:]))
d = sys.argv[1]; ang = float(sys.argv[2]) if len(sys.argv) > 2 else 50
by = collections.Counter(); byaxis = collections.defaultdict(collections.Counter); worlds = 0; tot = 0; strands = 0; examples = collections.defaultdict(list)
for f in sorted(glob.glob(os.path.join(d, "*.out.json"))):
    name = os.path.basename(f)[:-9]; worlds += 1
    j = json.load(open(f)); k_here = 0
    for p in j["pieces"]:
        for si, s in enumerate(p["strands"]):
            if len(s) < 3: continue
            strands += 1
            L = length(s)
            for arc, x, z, deg in kinks(s, ang=ang):
                fe = min(arc, L - arc); near = p["a"] if arc <= L - arc else p["b"]
                kind = "tanglecable" if p["a"].startswith("tangle:(") else (near or "?").split(":")[0]
                band = "<0.25" if fe < .25 else "<0.75" if fe < .75 else ">=0.75"
                by[(kind, band)] += 1; k_here += 1
                if len(examples[(kind, band)]) < 3: examples[(kind, band)].append((name, p["a"], p["b"], si, round(fe, 2), deg, x, z))
    tot += k_here
    for part in name.split("_"): byaxis[part[0]][part] += k_here
print("worlds", worlds, "strands", strands, "kinks", tot)
for k, v in sorted(by.items(), key=lambda kv: -kv[1]): print(" ", k, v, examples[k][:2])
for ax, c in byaxis.items(): print(" axis", ax, dict(c))
