#!/usr/bin/env python3
"""The Modern bucket as an orange pail (MODERN_BOTTLE_REDRAW_SODA_AND_ORANGE_PAIL); the Modern bottle stays the pilot.

Owner 2026-10-24: "Modern bottle should look soda-like. Modern bucket should be orange."

The pail is a repaint of the installed pilot sprite (v1/out/<Size>/Modern, LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS), not
redraws: the alpha channel and the CutoutComplex mask (R = liquid -> the liquid's colour, G = trim -> the Stuff colour, owner
by card 2026-10-16) are kept byte for byte, so the liquid and trim tinting work exactly as before. Only painted body pixels
move, never a liquid or trim pixel.

Bottle: the soda repaint (cola-red label, white swoosh) shipped in f17e02293b and the owner ruled it out on the review
sheet: "I like the before bottles but the after buckets on the review sheet". The installed Modern bottle is the pilot
again, byte for byte, and its code is gone from here; only the pail is built.

Bucket: the painted body (the blue of the original, by hue weight) is recoloured to a hardware-store safety orange, value
lifted so the orange is bright; white glints, the grey liquid and the trim (rim, handle) are not blue and stay.

    python3 modern_soda_pail.py <out_dir>    # <out_dir>/<rel> for the pail + preview.png
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
SRC = HERE / "v1" / "out"
REL = {"Bottle": "Things/Item/Resource/FlowWorks/Modern/RM_Bottle.png",   # installed == the pilot (owner, see above)
       "Bucket": "Things/Item/Resource/FlowWorks/Modern/RM_Bucket.png"}

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


BUILD = {"Bucket": build_bucket}

PAIL_ORANGE_MIN = 0.70   # share of the painted body that is orange
PAIL_BLUE_MAX = 0.01


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
    pv = Image.new("RGBA", (256 * 2, 256), (70, 70, 70, 255))
    for i, size in enumerate(("Bucket",)):
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
