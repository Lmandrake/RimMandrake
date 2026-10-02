#!/usr/bin/env python3
"""Messy Conduit phase-1a placeholder textures (procedural PIL + numpy).

Jawa look: matte black cable, dark and ochre tape, no white anywhere, 70s-brown accents.
Usage:  export_textures.py --out <dir> [--sheet <png>]    write + validate
        export_textures.py --check <dir>                  validate only
Exit status is non-zero if any file FAILs.
"""
import argparse
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SS = 4  # supersample for drawn shapes

NAMES = {
    "ConduitTransparent.png": (32, 32), "Strand_Jawa.png": (128, 32), "StrandShadow.png": (128, 32),
    "Junction_Tape.png": (64, 64), "Junction_Tin.png": (64, 64), "Plug.png": (64, 64),
    "EndFrayed_Dead.png": (64, 64), "EndFrayed_Live.png": (64, 64), "StubWall.png": (64, 64),
    "StubRock.png": (64, 64), "PowerStrip.png": (64, 32), "SparkGlow.png": (64, 64),
}
STRIPS = ("Strand_Jawa.png", "StrandShadow.png")


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def to_img(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")


# ---------------------------------------------------------------- strips
def strand_jawa():
    W, H = 128, 32
    x = np.arange(W)[None, :].astype(float)
    y = np.arange(H)[:, None].astype(float)
    c, r = 15.5, 10.5
    d = np.abs(y - c) + 0 * x
    alpha = np.clip(r + 0.5 - d, 0, 1)
    n = (y - c) / r + 0 * x                      # -1 top .. +1 bottom
    # top-lit cylinder: broad low sheen slightly above centre, darker toward the bottom edge
    sheen = np.exp(-((n + 0.28) / 0.45) ** 2)
    under = np.clip(n, 0, 1) ** 2
    two_pi = 2 * math.pi
    wear = (0.5 * np.sin(two_pi * 3 * x / W + 1.1) + 0.5 * np.sin(two_pi * 7 * x / W + 0.4)
            + 0.35 * np.sin(two_pi * 13 * x / W + 2.2) * np.cos(two_pi * 2 * y / H))
    lum = 0.20 + 0.80 * sheen * (1 + 0.10 * wear) - 0.25 * under + 0.025 * wear
    lum = np.clip(lum, 0, 1)
    dark, hi = np.array(hx("#1c1b19"), float), np.array(hx("#3a3833"), float)
    rgb = dark[None, None, :] + (hi - dark)[None, None, :] * lum[..., None]
    out = np.dstack([rgb, alpha * 255])
    return to_img(out)


def strand_shadow():
    W, H = 128, 32
    x = np.arange(W)[None, :].astype(float)
    y = np.arange(H)[:, None].astype(float)
    a = 110 * np.exp(-((y - 16.5) / 5.5) ** 2) * (1 + 0.06 * np.sin(2 * math.pi * 2 * x / W)) + 0 * x
    out = np.zeros((H, W, 4))
    out[..., 3] = a
    return to_img(out)


# ---------------------------------------------------------------- helpers for 64x64 art
def canvas(w, h):
    return Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))


def down(im):
    w, h = im.size
    return im.resize((w // SS, h // SS), Image.LANCZOS)


def S(v):
    if isinstance(v, (list, tuple)):
        return [S2(p) for p in v]
    return max(1, int(round(v * SS)))


def S2(p):
    return tuple(q * SS for q in p) if isinstance(p, (list, tuple)) else p * SS


def mask_of(draw_fn, w, h):
    m = Image.new("L", (w * SS, h * SS), 0)
    draw_fn(ImageDraw.Draw(m))
    return m


def lit(im, hmask=None, blur=3.0, k=0.9, soft=0.0):
    """Top-lit relief shading from the alpha (or a given mask) blurred into a height field."""
    a = np.asarray(im).astype(float)
    src = Image.fromarray((a[..., 3]).astype(np.uint8)) if hmask is None else hmask
    h = np.asarray(src.filter(ImageFilter.GaussianBlur(blur * SS))).astype(float) / 255.0
    gy, gx = np.gradient(h)
    g = gy * 0.9 + gx * 0.25
    g = g / (np.abs(g).max() + 1e-9)
    f = 1 + k * g + soft * (h - 0.5)
    a[..., :3] = a[..., :3] * f[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


def fill_through(mask, color):
    im = Image.new("RGBA", mask.size, color + (255,))
    im.putalpha(mask)
    return im


def noise_mod(im, amp=0.10, scale=3.0, seed=1):
    rng = np.random.RandomState(seed)
    w, h = im.size
    n = rng.rand(h // int(scale * SS) + 2, w // int(scale * SS) + 2)
    n = Image.fromarray((n * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    n = (np.asarray(n).astype(float) / 255 - 0.5) * 2 * amp
    a = np.asarray(im).astype(float)
    a[..., :3] *= (1 + n)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


def wobbly_ellipse(cx, cy, rx, ry, rng, wob=0.08, n=40):
    pts = []
    ph = [rng.uniform(0, 6.28) for _ in range(3)]
    for i in range(n):
        t = 2 * math.pi * i / n
        k = 1 + wob * (math.sin(2 * t + ph[0]) + 0.6 * math.sin(3 * t + ph[1]) + 0.4 * math.sin(5 * t + ph[2]))
        pts.append(((cx + rx * k * math.cos(t)) * SS, (cy + ry * k * math.sin(t)) * SS))
    return pts


# ---------------------------------------------------------------- 64x64 items
def junction_tape():
    rng = random.Random(3)
    W = H = 64
    m = mask_of(lambda d: (
        d.polygon(wobbly_ellipse(32, 29, 19, 13, rng), fill=255),
        d.polygon(wobbly_ellipse(32, 41, 8.5, 11, rng, 0.1), fill=255),   # stem of the T
        d.polygon(wobbly_ellipse(23, 30, 9, 9, rng, 0.12), fill=255),
        d.polygon(wobbly_ellipse(41, 30, 9, 9, rng, 0.12), fill=255)), W, H)
    cols = [hx("#1a1917"), hx("#8a6a2a"), hx("#3a3128"), hx("#8a6a2a"), hx("#4e4230")]
    arr = np.zeros((H * SS, W * SS, 3))
    yy, xx = np.mgrid[0:H * SS, 0:W * SS] / SS
    u = (xx * 0.8 + yy * 0.6) + 1.3 * np.sin(yy * 0.5) + 0.8 * np.sin(xx * 0.9)
    idx = (np.floor(u / 4.2).astype(int)) % len(cols)
    for i, c in enumerate(cols):
        arr[idx == i] = c
    im = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
    im.putalpha(m)
    im = noise_mod(im, 0.12, 2.0, 5)
    im = lit(im, blur=4.5, k=1.1, soft=0.2)
    # grease sheen: dark outline
    edge = m.filter(ImageFilter.MaxFilter(3 * SS + 1))
    return down(Image.alpha_composite(fill_through(edge, hx("#0c0b0a")), im))


def junction_tin():
    rng = random.Random(7)
    W = H = 64
    box = (10, 12, 54, 52)
    m = mask_of(lambda d: d.rounded_rectangle(S(box), radius=S(5), fill=255), W, H)
    im = fill_through(m, hx("#3c3a34"))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(S(box), radius=S(5), outline=hx("#7a786c") + (255,), width=S(2))
    d.rounded_rectangle(S((13, 15, 51, 49)), radius=S(3), outline=hx("#24221e") + (255,), width=S(1))
    # dents: dark pits with lighter lower lip
    for cx, cy, r in ((20, 22, 6), (44, 40, 7), (36, 18, 4), (24, 44, 4)):
        d.ellipse(S((cx - r, cy - r, cx + r, cy + r)), fill=hx("#2a2824") + (255,))
        d.arc(S((cx - r, cy - r, cx + r, cy + r)), 20, 160, fill=hx("#6a685c") + (255,), width=S(1.2))
    # ochre tape strip across the lid
    d.polygon(S([(27, 10), (35, 10), (38, 54), (30, 54)]), fill=hx("#8a6a2a") + (255,))
    d.line(S([(28, 10), (31, 54)]), fill=hx("#a88338") + (255,), width=S(1.2))
    d.line(S([(34, 10), (37, 54)]), fill=hx("#5e4818") + (255,), width=S(1.2))
    im.putalpha(Image.fromarray(np.minimum(np.asarray(im.getchannel("A")), np.asarray(m))))
    im = noise_mod(im, 0.08, 1.5, 9)
    im = lit(im, blur=2.5, k=0.7)
    return down(im)


def plug():
    W = H = 64
    im = canvas(W, H)
    d = ImageDraw.Draw(im)
    # prongs (dull steel)
    for y0 in (24.5, 35.5):
        d.rectangle(S((44, y0, 58, y0 + 4)), fill=hx("#6e7072") + (255,))
        d.line(S([(44, y0 + 0.6), (58, y0 + 0.6)]), fill=hx("#9a9a8e") + (255,), width=S(1))
    # strain relief taper at left
    d.polygon(S([(2, 28), (14, 24), (14, 40), (2, 36)]), fill=hx("#1e1d1b") + (255,))
    for x in (5, 8, 11):
        d.line(S([(x, 26.5), (x, 37.5)]), fill=hx("#0c0b0a") + (255,), width=S(1))
    # chunky casing
    d.rounded_rectangle(S((13, 17, 45, 47)), radius=S(6), fill=hx("#2e2c28") + (255,))
    d.rounded_rectangle(S((13, 17, 45, 47)), radius=S(6), outline=hx("#0e0d0c") + (255,), width=S(1.5))
    d.rectangle(S((40, 21, 45, 43)), fill=hx("#3d3a34") + (255,))   # front face plate
    d.line(S([(18, 20.5), (40, 20.5)]), fill=hx("#55524a") + (255,), width=S(1.5))   # top sheen
    d.line(S([(18, 44), (40, 44)]), fill=hx("#14130f") + (255,), width=S(1.5))
    im = noise_mod(im, 0.07, 1.5, 11)
    im = lit(im, blur=2.2, k=0.6)
    return down(im)


def _fray(live):
    W = H = 64
    rng = random.Random(21 if live else 22)
    im = canvas(W, H)
    # soot behind the end for the live one
    if live:
        sm = mask_of(lambda d: d.ellipse(S((22, 18, 54, 46)), fill=150), W, H).filter(ImageFilter.GaussianBlur(4 * SS))
        im = Image.alpha_composite(im, fill_through(sm, hx("#0a0908")))
    # cable stub with cylinder shading, entering at left edge
    stub = canvas(W, H)
    sd = ImageDraw.Draw(stub)
    sd.rounded_rectangle(S((-4, 26, 35, 38)), radius=S(2), fill=hx("#1c1b19") + (255,))
    stub = lit(stub, blur=2.0, k=0.9)
    sd = ImageDraw.Draw(stub)
    sd.line(S([(0, 29), (33, 29)]), fill=hx("#3a3833") + (255,), width=S(1.6))
    sd.rectangle(S((33, 27, 36, 37)), fill=hx("#0f0e0d") + (255,))   # stripped jacket lip
    # insulation hint (ochre-brown tape bit) near the end
    sd.rectangle(S((28, 26, 31, 38)), fill=hx("#6a5424") + (255,))
    im = Image.alpha_composite(im, stub)
    d = ImageDraw.Draw(im)
    if live:
        cols = ["#d98a3c", "#f0a04a", "#ffb860", "#e0782c", "#ffcf70"]
    else:
        cols = ["#7a5838", "#8a6444", "#6a4c30", "#9a6a3c", "#74583e"]
    n = 9
    for i in range(n):
        ang = (i - (n - 1) / 2) / ((n - 1) / 2) * math.radians(38) + rng.uniform(-0.05, 0.05)
        ln = rng.uniform(12, 22)
        bend = rng.uniform(-0.35, 0.35)
        p0 = (36.0, 32.0 + (i - (n - 1) / 2) * 0.9)
        pts = []
        for t in np.linspace(0, 1, 14):
            a = ang + bend * t
            pts.append(((p0[0] + math.cos(ang) * ln * t * 0.7 + math.cos(a) * ln * t * 0.3) * SS,
                        (p0[1] + math.sin(ang) * ln * t * 0.7 + math.sin(a) * ln * t * 0.3) * SS))
        c = hx(cols[i % len(cols)])
        d.line(pts, fill=(int(c[0] * .55), int(c[1] * .55), int(c[2] * .55), 255), width=int(2.4 * SS))
        d.line(pts, fill=c + (255,), width=int(1.4 * SS))
    if live:
        sc = mask_of(lambda dd: dd.ellipse(S((30, 24, 46, 40)), fill=90), W, H).filter(ImageFilter.GaussianBlur(2.5 * SS))
        im = Image.alpha_composite(im, fill_through(sc, hx("#15110d")))
    return down(im)


def stub_wall():
    W = H = 64
    rng = random.Random(4)
    outer = mask_of(lambda d: d.ellipse(S((8, 12, 56, 52)), fill=255), W, H)
    hole = mask_of(lambda d: d.ellipse(S((20, 23, 44, 41)), fill=255), W, H)
    ring = Image.fromarray(np.clip(np.asarray(outer).astype(int) - np.asarray(hole).astype(int), 0, 255).astype(np.uint8))
    im = fill_through(outer, hx("#4a4d50"))
    im = noise_mod(im, 0.08, 1.5, 3)
    im = lit(im, hmask=ring, blur=2.2, k=1.0)
    d = ImageDraw.Draw(im)
    d.ellipse(S((8, 12, 56, 52)), outline=hx("#222426") + (255,), width=S(1.3))
    # black hole with a hint of depth
    d.ellipse(S((20, 23, 44, 41)), fill=hx("#050505") + (255,))
    d.arc(S((20, 23, 44, 41)), 200, 340, fill=hx("#0d0d0d") + (255,), width=S(1))
    d.arc(S((20, 23, 44, 41)), 20, 160, fill=hx("#5e6164") + (255,), width=S(1.2))
    for cx, cy in ((14, 32), (50, 32)):
        d.ellipse(S((cx - 2.2, cy - 2.2, cx + 2.2, cy + 2.2)), fill=hx("#2a2c2e") + (255,))
        d.ellipse(S((cx - 1.6, cy - 1.8, cx + 1.4, cy + 1.2)), fill=hx("#7c8084") + (255,))
    return down(im)


def stub_rock():
    W = H = 64
    rng = random.Random(9)
    n = 36
    outer, inner = [], []
    for i in range(n):
        t = 2 * math.pi * i / n
        chip = 1 + rng.uniform(-0.12, 0.12) + (0.14 if rng.random() < 0.15 else 0)
        outer.append(((32 + 21 * chip * math.cos(t)) * SS, (32 + 17 * chip * math.sin(t)) * SS))
        inner.append(((32 + 16 * math.cos(t)) * SS, (32 + 12.5 * math.sin(t)) * SS))
    om = mask_of(lambda d: d.polygon(outer, fill=255), W, H)
    hm = mask_of(lambda d: d.polygon(inner, fill=255), W, H)
    ring = Image.fromarray(np.clip(np.asarray(om).astype(int) - np.asarray(hm).astype(int), 0, 255).astype(np.uint8))
    im = fill_through(om, hx("#7a6a58"))
    im = noise_mod(im, 0.14, 1.2, 6)
    im = lit(im, hmask=ring, blur=1.8, k=1.1)
    d = ImageDraw.Draw(im)
    d.polygon(inner, fill=hx("#060505") + (255,))
    # lighter chipped lip on the upper rim
    for i in range(n):
        if 14 <= i <= 24:
            d.line([outer[i], outer[(i + 1) % n]], fill=hx("#a89880") + (255,), width=S(1.2))
    return down(im)


def power_strip():
    W, H = 64, 32
    im = canvas(W, H)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(S((3, 8, 61, 25)), radius=S(3), fill=hx("#3b3d3f") + (255,))
    im = lit(im, blur=2.0, k=0.9)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(S((3, 8, 61, 25)), radius=S(3), outline=hx("#17181a") + (255,), width=S(1.2))
    d.line(S([(6, 9.6), (58, 9.6)]), fill=hx("#5a5c5e") + (255,), width=S(1))
    for x in (8, 19, 30, 41):
        d.rounded_rectangle(S((x, 12, x + 8, 21)), radius=S(1.5), fill=hx("#121314") + (255,))
        d.rectangle(S((x + 2, 14, x + 3, 17.5)), fill=hx("#5c5e60") + (255,))
        d.rectangle(S((x + 5, 14, x + 6, 17.5)), fill=hx("#5c5e60") + (255,))
    glow = mask_of(lambda dd: dd.ellipse(S((50, 12, 58, 20)), fill=140), W, H).filter(ImageFilter.GaussianBlur(1.6 * SS))
    im = Image.alpha_composite(im, fill_through(glow, hx("#ff9a28")))
    d = ImageDraw.Draw(im)
    d.ellipse(S((52, 14, 56, 18)), fill=hx("#ffb020") + (255,))
    d.ellipse(S((53, 14.6, 54.6, 16.2)), fill=hx("#ffe08a") + (255,))
    return down(im)


def spark_glow():
    W = H = 64
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot(xx - 31.5, yy - 31.5) / 30.0
    t = np.clip(1 - r, 0, 1)
    a = (t ** 1.8) * 255
    core = np.clip(1 - r / 0.45, 0, 1)
    rgb = np.zeros((H, W, 3))
    orange, warm = np.array([255, 130, 28.]), np.array([255, 246, 190.])
    rgb[:] = orange + (warm - orange) * core[..., None]
    return to_img(np.dstack([rgb, a]))


def build_all():
    return {
        "ConduitTransparent.png": Image.new("RGBA", (32, 32), (0, 0, 0, 0)),
        "Strand_Jawa.png": strand_jawa(), "StrandShadow.png": strand_shadow(),
        "Junction_Tape.png": junction_tape(), "Junction_Tin.png": junction_tin(),
        "Plug.png": plug(), "EndFrayed_Dead.png": _fray(False), "EndFrayed_Live.png": _fray(True),
        "StubWall.png": stub_wall(), "StubRock.png": stub_rock(),
        "PowerStrip.png": power_strip(), "SparkGlow.png": spark_glow(),
    }


# ---------------------------------------------------------------- validation
def check(folder):
    fails = 0
    for name, (w, h) in NAMES.items():
        p = os.path.join(folder, name)
        why = []
        if not os.path.isfile(p):
            print(f"FAIL {name}: missing")
            fails += 1
            continue
        im = Image.open(p)
        if im.size != (w, h):
            why.append(f"size {im.size} != {(w, h)}")
        if im.mode != "RGBA":
            why.append(f"mode {im.mode}")
        if not why:
            a = np.asarray(im).astype(int)
            al = a[..., 3]
            if name == "ConduitTransparent.png":
                if a.any():
                    why.append("not all zero")
            else:
                if al.min() != 0 or al.max() < (100 if name == "StrandShadow.png" else 200):
                    why.append(f"alpha range {al.min()}..{al.max()}")
                if name in STRIPS:
                    if al[0].max() >= 10 or al[-1].max() >= 10:
                        why.append("top/bottom rows not transparent")
                    t = np.tile(a, (1, 4, 1)).astype(float)
                    seam = np.abs(t[:, 127] - t[:, 128]).mean()
                    allc = np.abs(np.diff(t, axis=1)).mean(axis=(0, 2))
                    inner = np.delete(allc, [127, 255, 383])
                    base = inner.mean()
                    if seam > max(2 * base, 0.5):
                        why.append(f"seam {seam:.2f} vs mean {base:.2f}")
                else:
                    corners = [al[0, 0], al[0, -1], al[-1, 0], al[-1, -1]]
                    if max(corners) != 0:
                        why.append(f"corner alpha {corners}")
        if why:
            fails += 1
            print(f"FAIL {name}: " + "; ".join(why))
        else:
            print(f"PASS {name}")
    return fails


def contact_sheet(folder, out):
    bgs = [(110, 80, 55), (28, 22, 18)]
    cells = []
    for name in NAMES:
        im = Image.open(os.path.join(folder, name)).convert("RGBA")
        if name in STRIPS:
            t = Image.new("RGBA", (im.width * 3, im.height))
            for i in range(3):
                t.paste(im, (i * im.width, 0))
            im = t
        cells.append((name, im.resize((im.width * 2, im.height * 2), Image.NEAREST)))
    cw = max(c[1].width for c in cells) + 10
    ch = max(c[1].height for c in cells) + 22
    cols = 3
    rows = (len(cells) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cw * 2, rows * ch), (60, 50, 42))
    for i, (name, im) in enumerate(cells):
        gx, gy = (i % cols) * cw * 2, (i // cols) * ch
        for j, bg in enumerate(bgs):
            tile = Image.new("RGBA", (cw, ch), bg + (255,))
            tile.alpha_composite(im, (5, 18))
            ImageDraw.Draw(tile).text((4, 3), name, fill=(240, 225, 190, 255))
            sheet.paste(tile.convert("RGB"), (gx + j * cw, gy))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet.save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--check")
    ap.add_argument("--sheet")
    a = ap.parse_args()
    folder = a.check or a.out
    if not folder:
        ap.error("need --out or --check")
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        for n, im in build_all().items():
            im.save(os.path.join(a.out, n))
    fails = check(folder)
    if a.sheet:
        contact_sheet(folder, a.sheet)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
