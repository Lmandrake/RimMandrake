"""Fit the TOP (and bottom) silhouette of an upright cylinder to an ellipse arc -> minor/major = sin(elevation).
usage: ellipse_fit.py <png> [x0 x1 y0 y1 crop in px]  ; alpha>=128 is solid.
Top arc: y(x) = cy - b*sqrt(1-((x-cx)/a)^2) for |x-cx| < 0.85a ; least squares over (cy, b) with a, cx from the width."""
import sys, math, os
LO, HI = float(os.environ.get('UMIN', 0)), float(os.environ.get('UMAX', 0.85))  # fit band in |u|; raise UMIN to skip a lid/cap
from PIL import Image
im = Image.open(sys.argv[1]).convert("RGBA")
if len(sys.argv) > 2:
    x0, x1, y0, y1 = map(int, sys.argv[2:6]); im = im.crop((x0, y0, x1, y1))
A = im.getchannel("A"); W, H = im.size; px = A.load()
cols = [x for x in range(W) if any(px[x, y] >= 128 for y in range(H))]
L, R = cols[0], cols[-1]
if os.environ.get("BODY_ROW"):   # take the body edges at one row (fittings on the sides would widen the silhouette)
    y = int(os.environ["BODY_ROW"]); xs = [x for x in range(W) if px[x, y] >= 128]; L, R = xs[0], xs[-1]
a = (R - L + 1) / 2; cx = (L + R) / 2
SIDE = os.environ.get("SIDE", "")   # 'L' or 'R': fit one half only, when the other carries a pipe/wheel
def fit(top):
    xs, ys = [], []
    for x in range(L, R + 1):
        u = (x - cx) / a
        if not (LO <= abs(u) <= HI) or (SIDE == 'L' and u > 0) or (SIDE == 'R' and u < 0): continue
        rng = range(H) if top else range(H - 1, -1, -1)
        y = next(y for y in rng if px[x, y] >= 128)
        xs.append(math.sqrt(1 - u * u)); ys.append(y)
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    k = sum((p - mx) * (q - my) for p, q in zip(xs, ys)) / sum((p - mx) ** 2 for p in xs)
    res = math.sqrt(sum((q - (my + k * (p - mx))) ** 2 for p, q in zip(xs, ys)) / n)
    return abs(k), res
bt, rt = fit(True); bb, rb = fit(False)
print(f"{sys.argv[1].split('/')[-1]}: width {2*a:.0f}px  top b/a={bt/a:.3f} (theta {math.degrees(math.asin(min(1,bt/a))):.0f} deg, rms {rt:.1f}px)"
      f"  bottom b/a={bb/a:.3f} (rms {rb:.1f}px)  height {H}px")
