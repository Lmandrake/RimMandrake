"""Kinks of a lab output classed as the bar reads a bend: hidden (under a wall or a machine's art), limp (a cut end's curl, within 1.0 of it),
forced (within 0.3 of a wall, another machine or furniture), else VISIBLE (unforced). usage: classify.py OUTDIR WORLDDIR | classify.py OUT.json WORLD.json"""
import json, sys, os, glob, math, collections
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from kink import kinks
def length(s): return sum(math.hypot(b[0]-a[0], b[1]-a[1]) for a, b in zip(s, s[1:]))
def rectdist(x0, z0, w, h, x, z):
    dx = max(x0 - x, 0, x - (x0 + w)); dz = max(z0 - z, 0, z - (z0 + h)); return math.hypot(dx, dz)
def classify(out, world):
    blocked = {(b[0], b[1]) for b in world["blocked"]}
    furn = {tuple(c) for c in world.get("furniture", [])}
    ms = world["machines"]
    res = []
    for p in out["pieces"]:
        for si, s in enumerate(p["strands"]):
            if len(s) < 3: continue
            L = length(s)
            for arc, x, z, deg in kinks(s):
                near_a = arc <= L - arc; fe = min(arc, L - arc)
                end = p["a"] if near_a else p["b"]
                kind = "pile" if p["a"].startswith("tangle:(") else (end or "pile").split(":")[0]
                cell = (math.floor(x), math.floor(z))
                if cell in blocked or any(m["x"] <= x <= m["x"] + m["w"] and m["z"] <= z <= m["z"] + m["h"] for m in ms): c = "hidden"
                elif kind == "terminal" and fe <= 1.0: c = "limp"
                elif any(rectdist(bx, bz, 1, 1, x, z) <= 0.3 for bx, bz in blocked | furn if abs(bx - x) < 2 and abs(bz - z) < 2) or \
                     any(rectdist(m["x"], m["z"], m["w"], m["h"], x, z) <= 0.3 for m in ms): c = "forced"
                else: c = "VISIBLE"
                res.append((c, kind, round(fe, 2), deg, p["a"], p["b"], x, z))
    return res
if __name__ == "__main__":
    a, b = sys.argv[1], sys.argv[2]
    pairs = [(a, b)] if a.endswith(".json") else [(f, os.path.join(b, os.path.basename(f)[:-9] + ".json")) for f in sorted(glob.glob(os.path.join(a, "*.out.json")))]
    rect = [float(v) for v in sys.argv[3].split(",")] if len(sys.argv) > 3 else None
    tot = collections.Counter(); kinds = collections.Counter(); ex = []
    for o, w in pairs:
        for r in classify(json.load(open(o)), json.load(open(w))):
            if rect and not (rect[0] <= r[6] <= rect[2] and rect[1] <= r[7] <= rect[3]): continue
            tot[r[0]] += 1
            if r[0] == "VISIBLE": kinds[r[1]] += 1; ex.append((os.path.basename(o),) + r[1:])
    print("classes", dict(tot), "| VISIBLE by end kind", dict(kinds))
    for e in ex[:int(os.environ.get("SHOW", "6"))]: print("  ", e)
