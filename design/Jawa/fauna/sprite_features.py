#!/usr/bin/env python3
"""Extract visual features from animal sprites so 1,260 creatures can be clustered
without a human looking at each one.

Reads   design/Jawa/fauna/sprites/*.png
        design/Jawa/fauna/animal_census.csv
Writes  design/Jawa/fauna/sprite_features.csv

Every feature is computed over NON-TRANSPARENT pixels only. A sprite is mostly empty
canvas, so any statistic taken over the whole image measures the transparency, not the
animal — that is the single easiest way to get confident nonsense here.
"""
import csv, math, os, sys, colorsys
from collections import Counter

try:
    from PIL import Image
except ImportError:
    sys.exit("PIL/Pillow required")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
FA   = os.path.join(ROOT, 'design', 'Jawa', 'fauna')
SPR  = os.path.join(FA, 'sprites')
OUT  = os.path.join(FA, 'sprite_features.csv')
ALPHA_MIN = 40          # below this a pixel is background, not the creature

def opaque_pixels(im):
    im = im.convert('RGBA')
    w, h = im.size
    px = im.load()
    pts = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a >= ALPHA_MIN:
                pts.append((x, y, r, g, b))
    return pts, w, h

def circular_mean_hue(hues, weights):
    """Hue is an angle; a plain mean of 350 deg and 10 deg gives 180 (cyan) for two reds."""
    if not hues: return 0.0
    sx = sum(w * math.cos(2 * math.pi * hu) for hu, w in zip(hues, weights))
    sy = sum(w * math.sin(2 * math.pi * hu) for hu, w in zip(hues, weights))
    if sx == 0 and sy == 0: return 0.0
    ang = math.atan2(sy, sx) / (2 * math.pi)
    return ang % 1.0

def hue_concentration(hues, weights):
    """1.0 = one pure hue, 0.0 = hue is all over the place. The resultant-vector length."""
    tot = sum(weights) or 1
    sx = sum(w * math.cos(2 * math.pi * hu) for hu, w in zip(hues, weights)) / tot
    sy = sum(w * math.sin(2 * math.pi * hu) for hu, w in zip(hues, weights)) / tot
    return math.hypot(sx, sy)

def features(path):
    im = Image.open(path)
    pts, w, h = opaque_pixels(im)
    if len(pts) < 12:
        return None
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    bw = max(xs) - min(xs) + 1; bh = max(ys) - min(ys) + 1

    hsv = [colorsys.rgb_to_hsv(p[2] / 255, p[3] / 255, p[4] / 255) for p in pts]
    hues = [c[0] for c in hsv]; sats = [c[1] for c in hsv]; vals = [c[2] for c in hsv]
    # weight hue by saturation*value: a near-grey pixel has a meaningless hue
    wt = [s * v for s, v in zip(sats, vals)]

    n = len(pts)
    mean_s = sum(sats) / n
    mean_v = sum(vals) / n
    hue = circular_mean_hue(hues, wt)
    conc = hue_concentration(hues, wt)

    # 12-bin hue histogram, saturation-weighted
    hist = [0.0] * 12
    for hu, ww in zip(hues, wt):
        hist[min(11, int(hu * 12))] += ww
    tw = sum(hist) or 1
    hist = [round(x / tw, 4) for x in hist]

    # shape
    fill = n / (bw * bh)
    aspect = bw / bh
    # perimeter proxy: opaque pixels with at least one transparent 4-neighbour
    occ = set((p[0], p[1]) for p in pts)
    perim = sum(1 for (x, y) in occ
                if (x+1, y) not in occ or (x-1, y) not in occ
                or (x, y+1) not in occ or (x, y-1) not in occ)
    # 1.0 = a disc; higher = spiky/limby. Normalised against a circle of equal area.
    spiky = perim / (2 * math.sqrt(math.pi * n)) if n else 0

    # bilateral symmetry about the bbox vertical axis
    cx = (min(xs) + max(xs)) / 2
    mirrored = sum(1 for (x, y) in occ if (int(round(2 * cx - x)), y) in occ)
    symmetry = mirrored / n

    # brightness contrast: is it flat-shaded or high-contrast?
    mv = mean_v
    contrast = math.sqrt(sum((v - mv) ** 2 for v in vals) / n)

    return dict(
        px=n, w=bw, h=bh, aspect=round(aspect, 3), fill=round(fill, 3),
        spiky=round(spiky, 3), symmetry=round(symmetry, 3),
        hue=round(hue, 4), hue_conc=round(conc, 3),
        sat=round(mean_s, 3), val=round(mean_v, 3), contrast=round(contrast, 3),
        hist=' '.join(f'{x:.3f}' for x in hist),
    )

def main():
    census = {}
    cp = os.path.join(FA, 'animal_census.csv')
    if os.path.exists(cp):
        for r in csv.DictReader(open(cp, encoding='utf-8')):
            census[r['defName']] = r
    files = sorted(f for f in os.listdir(SPR) if f.endswith('.png')) if os.path.isdir(SPR) else []
    rows, skipped = [], 0
    for fn in files:
        dn = fn[:-4]
        try:
            f = features(os.path.join(SPR, fn))
        except Exception as e:
            print(f"  ! {dn}: {e}", file=sys.stderr); skipped += 1; continue
        if not f:
            skipped += 1; continue
        c = census.get(dn, {})
        f.update(defName=dn, label=c.get('label', ''), mod=c.get('mod', ''),
                 bodySize=c.get('bodySize', ''), status=c.get('status', ''),
                 biomes_now=c.get('biomes_now', ''), intelligence=c.get('intelligence', ''))
        rows.append(f)
    if not rows:
        sys.exit("no sprites found yet — run after the extraction agents finish")
    cols = ['defName','label','mod','intelligence','bodySize','status','px','w','h','aspect','fill',
            'spiky','symmetry','hue','hue_conc','sat','val','contrast','hist','biomes_now']
    with open(OUT,'w',newline='',encoding='utf-8') as fh:
        wtr = csv.DictWriter(fh, fieldnames=cols, extrasaction='ignore')
        wtr.writeheader()
        for r in rows: wtr.writerow(r)
    print(f"wrote {OUT}: {len(rows)} sprites, {skipped} skipped (empty or unreadable)")

if __name__ == '__main__':
    main()
