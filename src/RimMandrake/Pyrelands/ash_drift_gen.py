#!/usr/bin/env python3
"""Procedural loose-ash drifts (Textures/Things/Filth/RM_FE_LooseAsh): one organic powder sheet per texture, domain-warped,
with a crisp ragged outline of coarse grain (sized to survive the ~2.5x downscale at play zoom) and stray specks past it,
so it reads as sifted ash, not blur and not a flat sticker. Usage: ash_drift_gen.py OUTDIR [seed] -> LooseAsh{A,B}{0..3}.png
at 256 px, plus mock.png (16x10 cells at 64 px, a third of cells with a drift). Shipped: seed 41."""
import sys, os, math
import numpy as np
from PIL import Image

N = 256

def fbm(rng, n, scales, stretch=1.0):
    out = np.zeros((n, n))
    amp = 1.0; tot = 0
    for s in scales:
        gw, gh = max(2, int(n / s / stretch)), max(2, int(n / s))
        g = rng.random((gh + 1, gw + 1))
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC)
        out += amp * (np.asarray(im, float) / 255.0)
        tot += amp; amp *= 0.55
    return out / tot

def rotate(a, ang):
    im = Image.fromarray((np.clip(a, 0, 1) * 65535).astype(np.uint16).astype(np.int32), mode="I")
    return np.asarray(im.rotate(ang, resample=Image.BILINEAR), float) / 65535.0

def drift(rng, kind):
    """One organic powder sheet: domain-warped noise inside a soft envelope, thin at the margin, heaped in places."""
    yy, xx = np.mgrid[0:N, 0:N].astype(float)
    cx, cy = N / 2 + rng.normal(0, 8, 2)
    sx = N * (0.36 if kind == "A" else 0.30); sy = sx * rng.uniform(0.40, 0.75)
    th = rng.uniform(0, np.pi)
    wx = (fbm(rng, N, [70, 30, 12]) - 0.5) * 70; wy = (fbm(rng, N, [70, 30, 12]) - 0.5) * 70
    dx, dy = xx + wx - cx, yy + wy - cy
    u = dx * np.cos(th) + dy * np.sin(th); v = -dx * np.sin(th) + dy * np.cos(th)
    env = np.exp(-((u / sx) ** 2 + (v / sy) ** 2) * 1.6)
    body = fbm(rng, N, [56, 24, 10, 5])
    d = env * (0.45 + 0.9 * body)
    if kind == "B":
        d *= 0.35 + 0.65 * np.clip((fbm(rng, N, [48, 18]) - 0.30) / 0.3, 0, 1)
    edge = np.clip(np.minimum(np.minimum(xx, N - 1 - xx), np.minimum(yy, N - 1 - yy)) / 24.0, 0, 1)
    return d * edge

def grain(rng, px):
    g = rng.random((N // px + 1, N // px + 1))
    return np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize(((N // px + 1) * px,) * 2, Image.NEAREST), float)[:N, :N] / 255.0

def render(rng, d):
    # Grain sized to survive the draw: 256 px drawn at about 100 px on screen, so 5-7 px texels are 2-3 screen px.
    g6 = grain(rng, 6); g4 = grain(rng, 4); g9 = grain(rng, 9)
    # a crisp but ragged outline: the sheet stops where density falls under a coarse-grained threshold (no fade-out)
    thr = 0.30 + 0.16 * (g6 - 0.5) + 0.08 * (g4 - 0.5)
    present = np.clip((d - thr) / 0.025, 0, 1)
    # a ring of stray specks just outside it, like sifted powder
    specks = (np.clip((d - 0.16) / 0.1, 0, 1) * (g4 > 0.80)) * 0.55
    dens = np.clip((d - 0.30) / 0.5, 0, 1)
    a = np.maximum(present * (0.62 + 0.28 * dens), specks)
    # powder fill: lighter heaps and greyer hollows at 9 px, fine 4 px tooth; char specks
    v = 0.74 + 0.10 * dens + 0.10 * (g9 - 0.5) + 0.06 * (g4 - 0.5)
    char = (grain(rng, 5) > 0.985) & (present > 0.5)
    v = np.where(char, v * 0.62, v)
    r = np.clip(v * 1.00, 0, 1); gch = np.clip(v * 0.975, 0, 1); b = np.clip(v * 0.94, 0, 1)
    out = np.stack([r, gch, b, np.clip(a, 0, 1)], -1)
    return Image.fromarray((out * 255).astype(np.uint8), "RGBA")

def main():
    outdir = sys.argv[1]; seed = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    rng = np.random.default_rng(seed)
    os.makedirs(outdir, exist_ok=True)
    tex = []
    for kind, idxs in (("A", [0, 1, 3]), ("B", [0, 1, 2, 3])):
        for i in idxs:
            im = render(rng, drift(rng, kind))
            im.save(os.path.join(outdir, "LooseAsh%s%d.png" % (kind, i)))
            tex.append(im)
    mock(rng, tex, os.path.join(outdir, "mock.png"))

def mock(rng, tex, path, cells=(16, 10), px=64, draw=float(os.environ.get("DRAW", "1.6")), tint=(184, 180, 172, 200), share=0.34):
    W, H = cells[0] * px, cells[1] * px
    base = np.zeros((H, W, 3))
    # deep ash ground stand-in: warm dark brown with soft mottling
    m = fbm(rng, max(W, H), [60, 20, 6])[:H, :W]
    for c, v in enumerate((34, 33, 33) if os.environ.get('SCARGROUND') else (62, 52, 45)):
        base[..., c] = v * (0.85 + 0.3 * m)
    img = Image.fromarray(base.astype(np.uint8)).convert("RGBA")
    size = int(px * draw)
    for cx in range(cells[0]):
        for cz in range(cells[1]):
            if rng.random() > share:
                continue
            for k in range(rng.integers(1, 3)):
                t = tex[rng.integers(len(tex))].resize((size, size), Image.BOX).rotate(rng.uniform(0, 360), Image.BILINEAR)
                arr = np.asarray(t, float)
                arr[..., 0] *= tint[0] / 255; arr[..., 1] *= tint[1] / 255; arr[..., 2] *= tint[2] / 255; arr[..., 3] *= tint[3] / 255
                t = Image.fromarray(arr.astype(np.uint8), "RGBA")
                ox = int(cx * px + px / 2 - size / 2 + rng.uniform(-0.45, 0.45) * px)
                oz = int(cz * px + px / 2 - size / 2 + rng.uniform(-0.45, 0.45) * px)
                img.alpha_composite(t, (max(0, ox), max(0, oz)))
    img.convert("RGB").save(path)

if __name__ == "__main__":
    main()
