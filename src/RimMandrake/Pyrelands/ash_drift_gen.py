#!/usr/bin/env python3
"""Procedural loose-ash drifts (Textures/Things/Filth/RM_FE_LooseAsh, def RM_FE_Filth_LooseAsh), 7 textures at 256 px.

Usage: ash_drift_gen.py OUTDIR [seed]  -> LooseAsh{A0,A1,A3,B0,B1,B2,B3}.png.  Shipped: seed 41 (2026-11-07 redraw).

Shapes are the seed-41 drift density fields of the previous cut, unchanged (drift() and the random stream are kept exactly, so
the same seed gives the same seven drifts); only the rendering changed. Each texture renders from its own stream,
default_rng(seed*1000 + index), so retuning the look never moves a shape.

What the render is for (judged at true scale: 64 px/cell, Graphic_Cluster's 0.8-1.2 size / 0-360 rotation / flip emulated,
trilinear mips as RimWorld loads mod textures, over a cleaned cut of real scar ground, by blind judges who were not told what
the patches were): the previous cut's soft, milky, evenly translucent fill and its fringe of 4-9 texel pixel blocks and stray
specks mip-blurred into haze and read as smoke or fog (smoke 4/5, ash 2/5). Opaque crisp drifts read as snow, cotton, stones
or decals instead; what reads as ash is a thin see-through powder (soil showing where it is thin), so that stays. This render:
  - edge: a defined rim from smooth noise (11-texel wobble, no pixel blocks), broken into crisp fragments of grit over the
    outer band, with coverage and value falling over the outer few texels so the powder thins and greys into the soil;
  - inside: crisp gritty clumps (7 texels) a little thicker and paler, and soil-showing thin spots (5.5 texels), sized to
    survive the ~2.5x downscale to screen; brighter where thick (heaped crest), 0.72 -> ~1.0 in value;
  - 5-10 dark charcoal flecks (4-6 texels, value 0.16: darker than the char ground, so they read as cinders, not holes;
    more than that read as pepper/mould);
  - warm grey (the def colour 184,180,172 multiplies it), never cream, never blue;
  - texture coverage 0.15-1.0, meant for the def's alpha 200 (the same art at alpha 255 read as snow pasted on).
RGB under transparent texels is char-dark so mip filtering never haloes light; no alpha below 8/255 (no faint fringe).
Blind-judge record, 8 rounds: Transient/ash_redraw/ (not in git). Best round: ash 4/5, smoke 1/5, old cut ash 2/5, smoke 4/5.
"""
import os
import sys

import numpy as np
from PIL import Image

N = 256
SS = 4            # geometry at 4x, premultiplied box-down to 256: one-texel antialiased edges
S = N * SS
BG = 0.15         # rgb under alpha 0

P = dict(t0=0.27, t0_j=0.05, edge_feat=11, band=0.14, frag=0.40, frag_c=0.34,
         c0=0.52, c_span=0.40, clump_t=0.58, clump_c=0.24, hole_t=0.30, hole_k=0.30, grit=7.0, grit2=5.5,
         v0=0.72, v_span=0.18, v_clump=0.05, crest=0.10,
         chars=(5, 10), char_r=(2.0, 3.2), char_v=0.16,
         edge_w=0.18, c_edge_k=0.45, v_edge_drop=0.14,
         warm=(1.0, 0.965, 0.925))


# ---- shapes: unchanged from the previous cut (seed 41 reproduces its seven drifts exactly) ----

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


def _skip_old_render(rng):
    """The previous cut's render drew four grain grids after each drift; draw the same so the next drift's shape is unchanged."""
    for px in (6, 4, 9, 5):
        rng.random((N // px + 1, N // px + 1))


# ---- render ----

def _smooth_noise(rng, feat_tex):
    g = max(2, int(N / feat_tex) + 3)
    a = rng.random((g, g)).astype(np.float32)
    im = Image.fromarray(a, "F").resize((int(g * feat_tex * SS), int(g * feat_tex * SS)), Image.BICUBIC)
    return np.asarray(im, float)[:S, :S]


def _up(a):
    return np.asarray(Image.fromarray(a.astype(np.float32), "F").resize((S, S), Image.BICUBIC), float)


def _ss(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def _down(rgba):
    a = rgba[..., 3:4]; pm = rgba[..., :3] * a
    red = lambda x: x.reshape(N, SS, N, SS, -1).mean((1, 3))
    A = red(a); Pm = red(pm)
    rgb = np.where(A > 1e-4, Pm / np.maximum(A, 1e-4), BG)
    A = np.where(A < 8 / 255, 0, A)
    return Image.fromarray(np.clip(np.dstack([rgb, A]) * 255 + 0.5, 0, 255).astype(np.uint8), "RGBA")


def render(rng, d256, p=P):
    d = _up(d256)
    t0 = p["t0"] + p["t0_j"] * (_smooth_noise(rng, p["edge_feat"]) - 0.5) * 2
    g1 = _smooth_noise(rng, p["grit"]); g2 = _smooth_noise(rng, p["grit2"]); g3 = _smooth_noise(rng, p["grit"] * 0.8)
    inner = d > t0 + p["band"]
    band = (d > t0) & ~inner
    # the rim breaks into crisp fragments of grit: in the outer band only the clumpier grit survives
    frag = band & (g3 > p["frag"] + 0.25 * (1 - (d - t0) / p["band"]))
    present = inner | frag
    dens = np.clip((d - p["t0"]) / 0.5, 0, 1)
    clump = _ss(p["clump_t"], p["clump_t"] + 0.04, g1)
    hole = _ss(p["hole_t"], p["hole_t"] - 0.04, g2)
    c = (p["c0"] + p["c_span"] * dens) * (1 - p["hole_k"] * hole) + p["clump_c"] * clump
    c = np.where(frag, np.maximum(c, p["frag_c"]), c)
    v = p["v0"] + p["v_span"] * dens + p["v_clump"] * clump - 0.03 * hole + p["crest"] * _ss(0.6, 0.8, dens)
    # charcoal flecks in the body
    yy, xx = np.nonzero(inner[::8, ::8])
    Y, X = np.ogrid[0:S, 0:S]
    for _ in range(min(int(rng.integers(*p["chars"])), len(yy))):
        i = rng.integers(len(yy)); y, x = yy[i] * 8, xx[i] * 8
        r = rng.uniform(*p["char_r"]) * SS; e = rng.uniform(0.45, 0.9)
        m = ((X - x) ** 2 + ((Y - y) / e) ** 2) < r * r
        v = np.where(m & inner, p["char_v"], v); c = np.where(m & inner, 0.9, c)
    # the powder thins and greys over the outer few texels; the rim itself stays defined
    e = _ss(0.0, p["edge_w"], d - t0)
    c = c * (p["c_edge_k"] + (1 - p["c_edge_k"]) * e)
    v = v - p["v_edge_drop"] * (1 - e)
    a = present * np.clip(c, 0, 1)
    v = np.where(present, np.clip(v, 0, 1), BG)
    w = p["warm"]
    return _down(np.dstack([np.stack([v * w[0], v * w[1], v * w[2]], -1), a]))


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    outdir = sys.argv[1]; seed = int(sys.argv[2]) if len(sys.argv) > 2 else 41
    os.makedirs(outdir, exist_ok=True)
    shape_rng = np.random.default_rng(seed)
    k = 0
    for kind, idxs in (("A", [0, 1, 3]), ("B", [0, 1, 2, 3])):
        for i in idxs:
            d = drift(shape_rng, kind)
            _skip_old_render(shape_rng)
            im = render(np.random.default_rng(seed * 1000 + k), d)
            im.save(os.path.join(outdir, "LooseAsh%s%d.png" % (kind, i)))
            print("LooseAsh%s%d" % (kind, i), im.getbbox())
            k += 1


if __name__ == "__main__":
    main()
