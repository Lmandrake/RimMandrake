#!/usr/bin/env python3
"""The Modern bottle as a soda bottle and the Modern bucket as an orange pail (MODERN_BOTTLE_REDRAW_SODA_AND_ORANGE_PAIL).

Owner 2026-10-24: "Modern bottle should look soda-like. Modern bucket should be orange."

Both are repaints of the installed pilot sprites (v1/out/<Size>/Modern, LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS), not
redraws: the alpha channel and the CutoutComplex mask (R = liquid -> the liquid's colour, G = trim -> the Stuff colour, owner
by card 2026-10-16) are kept byte for byte, so the liquid and trim tinting work exactly as before. Only painted body pixels
move, never a liquid or trim pixel.

Bottle: the contour PET shape and petaloid base were already a soda bottle's; what read as "a bottle of something" was the
label, a red/yellow/teal party swirl. The label band (fixed by the original's saturated, unmasked pixels) is repainted as
soda trade dress -- deep cola red with one white wave ribbon, shaded as a cylinder with a soft vertical highlight, no text
-- and nothing else: the liquid already carries the original's carbonation dots, which read as fizz in any liquid colour
(the liquid tint multiplies over them).

Bucket: the painted body (the blue of the original, by hue weight) is recoloured to a hardware-store safety orange, value
lifted so the orange is bright; white glints, the grey liquid and the trim (rim, handle) are not blue and stay.

    python3 modern_soda_pail.py <out_dir>    # <out_dir>/<rel> for both pieces + preview.png
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
SRC = HERE / "v1" / "out"
REL = {"Bottle": "Things/Item/Resource/FlowWorks/Modern/RM_Bottle.png",
       "Bucket": "Things/Item/Resource/FlowWorks/Modern/RM_Bucket.png"}

LABEL_ROWS = (84, 156)           # the label band lies in these rows of the 256 px bottle
COLA = np.array([0.74, 0.05, 0.06])
WHITE = np.array([0.97, 0.96, 0.94])
RIBBON_W = 0.13                  # ribbon half-width, in label heights
ORANGE_H = 27 / 360
BLUE_H, BLUE_CORE, BLUE_EDGE = 215 / 360, 35 / 360, 55 / 360


def load(size):
    d = SRC / size / "Modern"
    im = np.asarray(Image.open(d / f"RM_{size}.png").convert("RGBA")).astype(float) / 255.0
    m = np.asarray(Image.open(d / f"RM_{size}_m.png").convert("RGBA"))
    return im, m


def hsv(rgb):
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = np.maximum(mx - mn, 1e-6)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h = np.where(mx == r, ((g - b) / d) % 6.0, np.where(mx == g, (b - r) / d + 2.0, (r - g) / d + 4.0)) / 6.0
    h = np.where(mx - mn > 1e-6, h, 0.0)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    return h, s, mx


def hsv_to_rgb(h, s, v):
    i = np.floor(h * 6.0).astype(int) % 6
    f = h * 6.0 - np.floor(h * 6.0)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    out = np.zeros(h.shape + (3,))
    for k, (a, b, c) in enumerate(((v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q))):
        sel = i == k
        out[sel, 0], out[sel, 1], out[sel, 2] = a[sel], b[sel], c[sel]
    return out


def label_region():
    """Bool mask of the bottle's label band, from the original: saturated, opaque, neither liquid nor trim, closed."""
    im, m = load("Bottle")
    _, s, _ = hsv(im[..., :3])
    y = np.arange(im.shape[0])[:, None]
    lab = (s > 0.35) & (im[..., 3] > 0.5) & (m[..., 0] < 128) & (m[..., 1] < 128)
    lab &= (y >= LABEL_ROWS[0]) & (y < LABEL_ROWS[1])
    li = Image.fromarray((lab * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    return (np.asarray(li) > 127) & (im[..., 3] > 0.5) & (m[..., 0] < 128) & (m[..., 1] < 128)


def _smooth(x, w):
    return np.clip(0.5 + x / w, 0.0, 1.0)


def build_bottle():
    im, m = load("Bottle")
    rgb = im[..., :3].copy()
    lab = label_region()
    h, w = lab.shape
    # label coordinates, smoothed so the ribbon is one clean curve (the cut-out band's own edges are ragged by a pixel):
    # u across the whole band (its sides are vertical here), v from a moving-average top and bottom edge per column
    cols = np.where(lab.any(0))[0]
    x0, x1 = cols.min(), cols.max() + 1
    top = np.array([np.where(lab[:, x])[0].min() for x in cols], float)
    bot = np.array([np.where(lab[:, x])[0].max() + 1 for x in cols], float)
    k = np.ones(15) / 15
    top = np.convolve(np.pad(top, 7, mode="edge"), k, "valid")
    bot = np.convolve(np.pad(bot, 7, mode="edge"), k, "valid")
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    u = np.clip((xx - x0) / (x1 - x0), 0, 1)
    tt, bb = np.zeros(w), np.ones(w)
    tt[cols], bb[cols] = top, bot
    v = np.clip((yy - tt[None, :]) / np.maximum(bb - tt, 1)[None, :], 0, 1)
    shade = 0.50 + 0.50 * np.sin(np.pi * np.clip(u, 0, 1)) ** 0.6
    hi = 0.30 * np.exp(-((u - 0.30) / 0.07) ** 2)
    centre = 0.50 + 0.24 * np.sin(np.pi * (2 * u - 1))          # one S-swoosh across the visible face
    ribbon = _smooth(RIBBON_W * (0.6 + 0.6 * np.sin(np.pi * u)) - np.abs(v - centre), 0.035)   # tapered ends
    paint = COLA[None, None] * (1 - ribbon[..., None]) + WHITE[None, None] * ribbon[..., None]
    paint = paint * shade[..., None]
    paint = paint + (1 - paint) * hi[..., None]
    rgb[lab] = paint[lab]
    return _img(rgb, im)


def blue_weight(rgb):
    h, s, _ = hsv(rgb)
    dist = np.abs(h - BLUE_H)
    dist = np.minimum(dist, 1 - dist)
    return (1 - np.clip((dist - BLUE_CORE) / (BLUE_EDGE - BLUE_CORE), 0, 1)) * np.clip((s - 0.18) / 0.20, 0, 1)


def build_bucket():
    im, m = load("Bucket")
    rgb = im[..., :3]
    wt = blue_weight(rgb) * (m[..., 0] < 128) * (m[..., 1] < 128)
    _, s, v = hsv(rgb)
    orange = hsv_to_rgb(np.full(v.shape, ORANGE_H), np.clip(0.30 + 0.70 * s, 0, 0.95), np.clip(0.16 + 0.95 * v, 0, 1))
    out = rgb * (1 - wt[..., None]) + orange * wt[..., None]
    return _img(out, im)


def _img(rgb, im):
    a = np.round(im[..., 3] * 255).astype(np.uint8)
    return Image.fromarray(np.dstack([np.clip(np.round(rgb * 255), 0, 255).astype(np.uint8), a]), "RGBA")


BUILD = {"Bottle": build_bottle, "Bucket": build_bucket}

LABEL_RED_MIN = 0.55     # share of the label that is cola red
LABEL_WHITE = (0.12, 0.40)  # share of the label that is the white ribbon
LABEL_OTHER_MAX = 0.02   # share of the label in any other saturated hue (the old swirl's yellow, teal, orange)
PAIL_ORANGE_MIN = 0.70   # share of the painted body that is orange
PAIL_BLUE_MAX = 0.01


def bottle_reads_as_soda(img):
    """(ok, red, white, other) over the original's label band: cola red with a white ribbon and no other hue. FAILS on the
    original (multicolour swirl label: red 0.31, yellow/teal/orange 0.58, no white)."""
    a = np.asarray(img.convert("RGBA")).astype(float) / 255.0
    lab = label_region()
    h, s, v = hsv(a[..., :3])
    hd = np.minimum(h, 1 - h)
    red = float(((hd < 15 / 360) & (s > 0.6) & (v > 0.25))[lab].mean())
    white = float(((s < 0.15) & (v > 0.75))[lab].mean())
    other = float(((hd > 25 / 360) & (s > 0.4) & (v > 0.25))[lab].mean())
    ok = red >= LABEL_RED_MIN and LABEL_WHITE[0] <= white <= LABEL_WHITE[1] and other <= LABEL_OTHER_MAX
    return ok, red, white, other


def pail_is_orange(img):
    """(ok, orange, blue) over the bucket's painted body (opaque, saturated, neither liquid nor trim): FAILS on the blue
    original."""
    a = np.asarray(img.convert("RGBA")).astype(float) / 255.0
    _, m = load("Bucket")
    h, s, v = hsv(a[..., :3])
    body = (a[..., 3] > 0.5) & (m[..., 0] < 128) & (m[..., 1] < 128) & (s > 0.3)
    if body.sum() < 500:
        return False, 0.0, 1.0
    orange = float(((h > 18 / 360) & (h < 40 / 360) & (s > 0.55) & (v > 0.45))[body].mean())
    blue = float(((h > 180 / 360) & (h < 260 / 360))[body].mean())
    return orange >= PAIL_ORANGE_MIN and blue <= PAIL_BLUE_MAX, orange, blue


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    out = Path(argv[0] if argv else ".")
    pv = Image.new("RGBA", (256 * 4, 256), (70, 70, 70, 255))
    for i, size in enumerate(("Bottle", "Bucket")):
        im = BUILD[size]()
        dst = out / REL[size]
        dst.parent.mkdir(parents=True, exist_ok=True)
        im.save(dst)
        pv.alpha_composite(Image.open(SRC / size / "Modern" / f"RM_{size}.png").convert("RGBA"), (512 * i, 0))
        pv.alpha_composite(im, (512 * i + 256, 0))
        print(dst)
    pv.save(out / "preview.png")


if __name__ == "__main__":
    main()
