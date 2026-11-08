"""Pyrelands weather overlay textures (tileable 512x512 RGBA), drawn by WeatherOverlay_RM_* in Source/PyrelandsWeatherOverlays.cs.

Vanilla's rain and snow overlays are light streaks and flakes on an additive-looking veil: on this biome's dark ground and dim
black-rain sky they do not show at all, in a still or in motion (captured 2026-11-08, map w at noon: vanilla Rain, black rain,
ash fall on SnowHard, all showed no drop or flake at 47 px per cell). These are alpha-blended instead, so a dark drop reads
as dark on bright grass and a pale flake as pale on dark ash.

The whole-map plane repeats a texture every 10 cells, so 512 px is about 51 px a cell.
  RM_FE_BlackRainStreaks.png  thin sooty streaks falling down and a little left (the panner's (-0.25,-1)).
  RM_FE_AshFlakes.png         soft grey flakes of mixed size, a few torn ones, for a slow sideways drift.

python3 src/RimMandrake/Pyrelands/weather_overlay_gen.py [OUTDIR]
"""
import os, sys
import numpy as np
from PIL import Image, ImageFilter

N = 512
HERE = os.path.dirname(os.path.abspath(__file__))


def _stamp(acc, col, x, y, a, rgb):
    """Max-blend one pixel's alpha with wraparound, keep the colour of the strongest stamp."""
    xi, yi = int(x) % N, int(y) % N
    if a > acc[yi, xi]:
        acc[yi, xi] = a
        col[yi, xi] = rgb


def streaks(seed=11, count=150):
    rng = np.random.default_rng(seed)
    acc = np.zeros((N, N), np.float32)
    col = np.zeros((N, N, 3), np.float32)
    dx, dy = -0.25, 1.0                       # PNG y runs down: down and a little left
    norm = (dx * dx + dy * dy) ** 0.5
    dx, dy = dx / norm, dy / norm
    for _ in range(count):
        x0, y0 = rng.uniform(0, N), rng.uniform(0, N)
        length = rng.uniform(36, 84)
        peak = rng.uniform(0.7, 0.95)
        shade = rng.uniform(8, 24)
        rgb = (shade * 1.12, shade, shade * 0.9)
        steps = int(length * 3)
        for i in range(steps):
            t = i / steps
            a = peak * np.sin(np.pi * t) ** 0.6       # tapered at both ends
            x, y = x0 + dx * length * t, y0 + dy * length * t
            for ox, w in ((-1, 0.55), (0, 1.0), (1, 1.0), (2, 0.55)):   # about 3 px wide: thinner vanished on dark ash at play zoom
                _stamp(acc, col, x + ox, y, a * w, rgb)
    return acc, col


def flakes(seed=7, count=300):
    rng = np.random.default_rng(seed)
    acc = np.zeros((N, N), np.float32)
    col = np.zeros((N, N, 3), np.float32)
    yy, xx = np.mgrid[-14:15, -14:15]
    for _ in range(count):
        cx, cy = rng.uniform(0, N), rng.uniform(0, N)
        r = rng.choice([2.4, 3.2, 4.2, 5.4, 7.0], p=[0.25, 0.3, 0.25, 0.14, 0.06])
        stretch = rng.uniform(1.0, 1.8)               # some flakes torn long
        ang = rng.uniform(0, np.pi)
        ca, sa = np.cos(ang), np.sin(ang)
        u = (xx * ca + yy * sa) / stretch
        v = -xx * sa + yy * ca
        d = np.sqrt(u * u + v * v) / r
        a = np.clip(1.15 - d, 0, 1) ** 1.1 * rng.uniform(0.85, 1.0)
        shade = rng.uniform(170, 220)
        rgb = (shade, shade * 0.97, shade * 0.92)
        for (j, i) in zip(*np.nonzero(a > 0.01)):
            _stamp(acc, col, cx + xx[j, i], cy + yy[j, i], float(a[j, i]), rgb)
    return acc, col


def save(acc, col, path, blur=0.0):
    empty = acc <= 0                          # transparent texels take the mean colour, so a blur draws no dark or pale halo
    col = col.copy()
    col[empty] = col[~empty].mean(axis=0)
    rgba = np.zeros((N, N, 4), np.uint8)
    rgba[..., :3] = np.clip(col, 0, 255).astype(np.uint8)
    rgba[..., 3] = np.clip(acc * 255, 0, 255).astype(np.uint8)
    im = Image.fromarray(rgba, "RGBA")
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    im.save(path)
    return path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "Textures", "Weather")
    os.makedirs(out, exist_ok=True)
    print(save(*streaks(), os.path.join(out, "RM_FE_BlackRainStreaks.png"), blur=0.35))
    print(save(*flakes(), os.path.join(out, "RM_FE_AshFlakes.png"), blur=0.5))
