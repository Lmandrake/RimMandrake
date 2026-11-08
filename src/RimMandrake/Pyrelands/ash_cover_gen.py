#!/usr/bin/env python3
"""Loose-ash ground cover textures for SectionLayer_PyrelandsAsh (PyrelandsAshCover.cs), drawn with vanilla's terrain
fade-rough shader. Usage: ash_cover_gen.py TEXDIR TERRAINDIR -> TEXDIR/RM_FE_AshCover.png (the drift) and
RM_FE_AshCoverEdge.png (the shader's _AlphaAddTex, which frays the cover's edge). Shipped: this file's seeds.

The drift is the deep-ash terrain's own texture (TERRAINDIR/RM_FE_Ash_Deep.png), its value range lifted to pale ash (0.40-0.90,
a faint warm cast). The cover and the terrain both map their texture by world position, so the drift's ripples, pebbles and
char sticks lie exactly over the ground's: it reads as pale ash heaped in the same ripples (pass 21, map x, shots p21c2/p21r1-3).
A flat powder (pass 20's, kept below as powder()) read first as snow or frost to a second model and as concrete at play zoom;
a streaked powder read as mud. The edge noise is band-limited white noise filtered in the frequency domain, so it wraps
exactly: mid grain (12-60 cycles a tile, per channel) frays the margin into grit instead of a soft fade."""
import os
import sys
import numpy as np
from PIL import Image


def band(rng, n, lo, hi):
    f = np.fft.fftfreq(n) * n
    r = np.sqrt(f[:, None] ** 2 + f[None, :] ** 2)
    spec = np.fft.fft2(rng.standard_normal((n, n))) * ((r >= lo) & (r <= hi))
    out = np.real(np.fft.ifft2(spec))
    return out / (out.std() + 1e-9)


def powder(path, seed=11, n=512):
    rng = np.random.default_rng(seed)
    v = 0.72 + 0.025 * band(rng, n, 3, 10) + 0.02 * band(rng, n, 20, 60) + 0.018 * band(rng, n, 100, 256)
    yy, xx = np.mgrid[0:n, 0:n]
    for count, rad, val in ((40, (1.0, 1.8), 0.45), (60, (0.8, 1.4), 0.84)):   # cinder specks, pale flecks
        for _ in range(count):
            cx, cy, r = rng.uniform(0, n), rng.uniform(0, n), rng.uniform(*rad)
            dx = (xx - cx + n / 2) % n - n / 2
            dy = (yy - cy + n / 2) % n - n / 2
            m = np.clip(1 - np.sqrt(dx * dx + dy * dy) / r, 0, 1) ** 0.7
            v = v * (1 - m) + val * m
    rgb = (np.clip(v, 0, 1)[..., None] * np.array([1.0, 0.985, 0.96]) * 255).astype(np.uint8)
    Image.fromarray(np.dstack([rgb, np.full((n, n), 255, np.uint8)]), "RGBA").save(path)


def ripple(path, terrain_png):
    a = np.asarray(Image.open(terrain_png).convert("RGB")).astype(float) / 255
    lum = a.mean(axis=2)
    lo, hi = np.percentile(lum, 1), np.percentile(lum, 99)
    v = 0.40 + 0.5 * np.clip((lum - lo) / (hi - lo), 0, 1)
    rgb = (np.clip(v[..., None] * np.array([1.0, 0.975, 0.93]), 0, 1) * 255).astype(np.uint8)
    Image.fromarray(np.dstack([rgb, np.full(lum.shape, 255, np.uint8)]), "RGBA").save(path)


def edge(path, seed=3, n=256):
    rng = np.random.default_rng(seed)
    ch = [np.clip(128 + 60 * band(rng, n, 12, 60), 0, 255) for _ in range(3)]
    Image.fromarray(np.dstack(ch + [np.full((n, n), 255)]).astype(np.uint8), "RGBA").save(path)


if __name__ == "__main__":
    d = sys.argv[1]
    ripple(os.path.join(d, "RM_FE_AshCover.png"), os.path.join(sys.argv[2], "RM_FE_Ash_Deep.png"))
    edge(os.path.join(d, "RM_FE_AshCoverEdge.png"))
    print("wrote", d)
