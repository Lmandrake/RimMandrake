#!/usr/bin/env python3
"""
build_north.py — derive the 20 missing north files for bandolier_chewbacca and
bandolier_traveler in Star Wars KotOR Resources and Materials
(ws 3254370945, guy762.MM.KotORCore).

WHAT IS MISSING: each set ships east + south for all five body types and no
north and no north mask. 5 bodies x 2 files x 2 sets = 20. The def declares the
worn graphic through wornGraphicPath, always resolved as Graphic_Multi over
<path>_<BodyType>_<facing>, with no visibleFacing and no per-facing suppression
anywhere. Nothing declares north deliberately absent.

WHAT THE PLAYER SEES TODAY: not a missing bandolier. Graphic_Multi fills a null
north from the south at 180 degrees, so the pawn wears its CHEST POUCHES ON ITS
BACK, at drawData layer 65 which puts them on top of everything. Wrong art, never
absent art, and no log line is possible - so it reads as intentional and nobody
reports it.

THE TRANSFORM, measured off the author's own complete sets (survey_donor_north.py):

  1. MIRROR. bandolier_knife's north agrees with its mirrored south 77.4% by
     silhouette and with its unmirrored south only 34.3% - a strap over one
     shoulder swaps sides when you walk round the pawn. bandolier_double is an
     X-cross, 96% either way, so it neither confirms nor denies.

  2. THE BACK OF A BANDOLIER IS BARE LEATHER. Both of the author's norths are the
     strap with its front furniture gone: his bandolier_double north is an
     X-cross with the pouch blocks removed, his bandolier_knife north is a strap
     and belt with the knives removed. Pouches hang on the chest.

  3. HIS MASK SAYS WHICH PIXELS ARE WHICH, so none of that is guesswork.
     CutoutComplex tints mask-RED by the apparel's stuff colour and leaves
     mask-BLACK fixed. In both target sets the mask-black regions are exactly the
     ammo cells and the buckle, and the mask-red is the leather and the pouch.

WHY THIS IS A REPAINT AND NOT AN INPAINT - the first attempt, and why it failed.
The obvious build is "delete the mask-black furniture, grow the neighbours back
over the holes". It was written, run and REJECTED on sight: on chewbacca the ammo
cells cover 42% of the strap, so what grows back is not leather but the shadow
gaps between cells, and the result reads as a chewed, mottled band. There is no
clean strap surface to inpaint FROM.

So the band is repainted instead. The leather colour is sampled from the pixels
the author's own mask calls red INSIDE the strap - the gaps between his cells,
which is the only place his leather is visible - and a smooth across-the-band
ramp is built from that sample and laid down over the whole strap. The black
keyline is untouched, and so is every part that is not the strap.

  strap    = the largest interior component, i.e. the band inside the keyline
  keyline  = near-black outline pixels, kept exactly
  the rest = the hip pouch and any small parts, kept exactly

    /home/mandrake/.venvs/art/bin/python build_north.py
Output: the 20 textures, plus Source/REVIEW_north.png (run artifact, regenerable).
"""

import os
import sys
from collections import deque

from PIL import Image, ImageDraw, ImageFilter

DONOR = ("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/"
         "3254370945/Textures/SWApparel/Accessories")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_ROOT = os.path.join(os.path.dirname(HERE), "Textures", "SWApparel", "Accessories")
SHEET = os.path.join(HERE, "REVIEW_north.png")

SETS = ["bandolier_chewbacca", "bandolier_traveler"]
BODIES = ["Male", "Female", "Thin", "Fat", "Hulk"]

# Luminance at or below this is the author's black keyline, which is kept whole.
# Measured on both sets: the keyline sits at 0-24 and the darkest leather the
# mask calls red sits at 96, so anything in the 30s is safely a separator.
KEYLINE_L = 40


def lum(p):
    return (p[0] * 299 + p[1] * 587 + p[2] * 114) // 1000


def load(s, name):
    p = os.path.join(DONOR, s, name)
    return Image.open(p).convert("RGBA") if os.path.isfile(p) else None


def interior_components(art):
    """Connected regions of opaque, non-keyline pixels — the parts the keyline
    encloses. The strap is the biggest of them; the hip pouch is its own."""
    w, h = art.size
    px = art.load()
    seen = [[False] * w for _ in range(h)]
    comps = []
    for y in range(h):
        for x in range(w):
            p = px[x, y]
            if seen[y][x] or p[3] < 128 or lum(p) <= KEYLINE_L:
                continue
            q, comp = deque([(x, y)]), []
            seen[y][x] = True
            while q:
                cx, cy = q.popleft()
                comp.append((cx, cy))
                for nx, ny in ((cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)):
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx]:
                        np_ = px[nx, ny]
                        if np_[3] >= 128 and lum(np_) > KEYLINE_L:
                            seen[ny][nx] = True
                            q.append((nx, ny))
            comps.append(comp)
    comps.sort(key=len, reverse=True)
    return comps


def leather_ramp(art, mask, strap):
    """Build an across-the-band colour ramp from the leather the author drew.

    Only the strap pixels his mask paints RED are leather; the mask-black ones
    are ammo cells. Those red pixels are sorted by luminance and quantised into
    five stops, darkest at the band edge and lightest at its centre, which is how
    he shades every strap in the folder.
    """
    m = mask.convert("RGB")
    if m.size != art.size:
        m = m.resize(art.size, Image.NEAREST)
    ap, mp = art.load(), m.load()
    leather = [ap[x, y][:3] for (x, y) in strap if mp[x, y][0] >= 128]
    if len(leather) < 50:
        return None
    leather.sort(key=lum)
    stops = [leather[min(len(leather) - 1, int(len(leather) * f))]
             for f in (0.05, 0.25, 0.50, 0.75, 0.95)]
    return stops


def band_depth(art, strap):
    """How deep each strap pixel sits inside the band, 0 at the edge, 1 at the
    core. A cheap chamfer pass — the band is a few dozen pixels across, so exact
    Euclidean distance buys nothing a ramp would show."""
    sset = set(strap)
    depth = {}
    frontier = [p for p in strap
                if any((p[0]+dx, p[1]+dy) not in sset
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for p in frontier:
        depth[p] = 0
    q, d = deque(frontier), 0
    while q:
        d += 1
        nxt = deque()
        for (x, y) in q:
            for n in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                if n in sset and n not in depth:
                    depth[n] = d
                    nxt.append(n)
        q = nxt
    top = max(depth.values()) or 1
    return {p: v / top for p, v in depth.items()}


def repaint(art, mask):
    """Lay clean leather over the strap; keep the keyline, the pouch and alpha."""
    comps = interior_components(art)
    if not comps:
        return None, "no interior found inside the keyline"
    strap = comps[0]
    stops = leather_ramp(art, mask, strap)
    if stops is None:
        return None, "too little mask-red leather in the strap to sample"

    depth = band_depth(art, strap)
    out = art.copy()
    px = out.load()
    for p in strap:
        t = depth.get(p, 1.0)
        stop = stops[min(len(stops) - 1, int(t * len(stops)))]
        px[p[0], p[1]] = (stop[0], stop[1], stop[2], art.getpixel(p)[3])

    # One light smoothing pass so the five stops read as a gradient rather than
    # as terracing, applied to the strap only and never across its edges.
    blur = out.filter(ImageFilter.GaussianBlur(radius=1.2))
    bp = blur.load()
    for p in strap:
        if depth.get(p, 1.0) > 0.15:          # leave the edge stop crisp
            b = bp[p[0], p[1]]
            px[p[0], p[1]] = (b[0], b[1], b[2], art.getpixel(p)[3])
    return out, None


def alpha_count(im):
    return sum(1 for p in im.getdata() if p[3] > 0)


def build():
    made, cells, failures = [], [], []
    for s in SETS:
        out_dir = os.path.join(OUT_ROOT, s)
        os.makedirs(out_dir, exist_ok=True)
        for body in BODIES:
            south = load(s, f"Apparel_{body}_south.png")
            smask = load(s, f"Apparel_{body}_southm.png")
            if not (south and smask):
                failures.append(f"{s} {body}: donor south or southm missing")
                continue

            painted, err = repaint(south, smask)
            if err:
                failures.append(f"{s} {body}: {err}")
                continue
            north = painted.transpose(Image.FLIP_LEFT_RIGHT)

            # --- gates, before anything is written -----------------------
            if north.size != south.size:
                failures.append(f"{s} {body}: canvas drifted to {north.size}")
                continue
            if alpha_count(north) != alpha_count(south):
                failures.append(f"{s} {body}: silhouette changed — a repaint "
                                f"must not move alpha")
                continue
            if north.getchannel("A").getextrema()[1] != 255:
                failures.append(f"{s} {body}: no fully opaque pixel")
                continue
            changed = sum(1 for a, b in zip(south.transpose(Image.FLIP_LEFT_RIGHT).getdata(),
                                            north.getdata()) if a[:3] != b[:3])
            if changed < 0.10 * alpha_count(south):
                failures.append(f"{s} {body}: only {changed} px repainted — the "
                                f"furniture is still on the back")
                continue

            # After the repaint no fixed-colour furniture survives on this
            # facing, so the mask is a plain tint field. The author ships his own
            # north masks as a 16x16 solid red; this is the same thing at the
            # art's own canvas, where it cannot be mistaken for a truncated file.
            Image.new("RGBA", south.size, (255, 0, 0, 255)).save(
                os.path.join(out_dir, f"Apparel_{body}_northm.png"))
            north.save(os.path.join(out_dir, f"Apparel_{body}_north.png"))

            made.append((s, body, changed, alpha_count(south)))
            cells.append((f"{s.split('_')[1]} {body}", south, north))

    print(f"  {'set':<12}{'body':<8}{'repainted':>11}{'drawn':>9}{'share':>8}")
    for s, body, ch, n in made:
        print(f"  {s.split('_')[1]:<12}{body:<8}{ch:>11}{n:>9}{ch/n:>7.0%}")
    for f in failures:
        print(f"  REJECTED  {f}")
    print(f"\n  {2*len(made)} files written, {len(failures)} rejected")
    return cells, failures


def sheet(cells):
    cell = 190
    img = Image.new("RGBA", (cell * 2 + 150, cell * len(cells) + 30), (32, 32, 36, 255))
    d = ImageDraw.Draw(img)
    for i, t in enumerate(["south (the donor's)", "NORTH (ours)"]):
        d.text((150 + i * cell + 4, 8), t, fill=(220, 220, 210, 255))
    for r, (label, a, b) in enumerate(cells):
        y = 30 + r * cell
        d.text((6, y + cell // 2), label, fill=(200, 200, 190, 255))
        for i, im in enumerate([a, b]):
            t = im.copy()
            t.thumbnail((cell - 8, cell - 8))
            img.alpha_composite(t, (150 + i * cell + 4, y + 4))
    img.save(SHEET)
    print(f"  sheet -> {SHEET}")


def main():
    cells, failures = build()
    if cells:
        sheet(cells)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
