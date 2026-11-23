"""Kink measure for a laid strand: the turn accumulated over a short arc window. A kink is a turn of >= ANG degrees inside
WIN cells of arc length (a local radius of WIN/ANG_rad, far below the loose loop's typical radius)."""
import json, math, sys

def resample(pts, step=0.02):
    out = [pts[0]]
    acc = 0.0
    for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, z1 - z0)
        if L < 1e-9: continue
        t = step - acc
        while t <= L:
            out.append((x0 + (x1 - x0) * t / L, z0 + (z1 - z0) * t / L)); t += step
        acc = L - (t - step)
    if out[-1] != tuple(pts[-1]): out.append(tuple(pts[-1]))
    return out

def heading(a, b): return math.atan2(b[1] - a[1], b[0] - a[0])
def wrap(a): return (a + math.pi) % (2 * math.pi) - math.pi

def kinks(pts, win=0.12, ang=50.0, skip=0.0, step=0.02):
    """[(arc, x, z, deg)] local maxima of |turn over win| above ang, at least skip cells from either end."""
    r = resample(pts, step)
    n = len(r)
    if n < 4: return []
    hd = [heading(r[i], r[i + 1]) for i in range(n - 1)]
    k = max(1, int(round(win / step)))
    total = (n - 1) * step
    turns = []
    for i in range(len(hd) - k):
        t = sum(wrap(hd[j + 1] - hd[j]) for j in range(i, i + k - 1)) if k > 1 else 0
        turns.append(abs(t))
    res = []
    i = 0
    while i < len(turns):
        if math.degrees(turns[i]) >= ang:
            j = i
            while j + 1 < len(turns) and math.degrees(turns[j + 1]) >= ang: j += 1
            m = max(range(i, j + 1), key=lambda q: turns[q])
            arc = (m + k / 2) * step
            if arc >= skip and total - arc >= skip:
                c = r[m + k // 2]
                res.append((round(arc, 3), round(c[0], 3), round(c[1], 3), round(math.degrees(turns[m]), 1)))
            i = j + 1
        else:
            i += 1
    return res

if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    rect = [float(v) for v in sys.argv[2].split(",")] if len(sys.argv) > 2 else None
    tot = 0
    for p in d["pieces"]:
        for si, s in enumerate(p["strands"]):
            if len(s) < 2: continue
            if rect and not any(rect[0] <= x <= rect[2] and rect[1] <= z <= rect[3] for x, z in s): continue
            ks = kinks(s)
            if ks:
                tot += len(ks); print(p["a"], "|", p["b"], "strand", si, "len", len(s), ks)
    print("TOTAL kinks", tot)
