"""RM_WaterThin terrain texture: ankle-deep still fresh water over a wet silt pond bed (pond_depth_design §4, ruling D4).

A PLAIN tiled terrain picture (like vanilla Marsh), not a *Ramp for the Map/WaterDepth shader: the bed must show,
and a ramp carries no bed. Procedural and seamless by construction (all fields periodic; pebbles placed on a
wrapped torus). No game or donor pixels are copied; only target levels are measured from vanilla:
Mud mean RGB (74.5, 57.2, 45.5), WaterShallowRamp mean (87.4, 96.4, 98.8), Marsh (55.2, 61.8, 47.3).
The bed sits at a wet-darkened Mud level; a thin blue-grey veil (~40%) and faint still-water glints lie over it,
so the tile reads between WaterShallow (deeper, opaque) and Mud (no water).

    python3 src/RimMandrake/FlowWorks/art_source/WaterThin/make_water_thin.py <out.png>
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image

S = 1024
SEED = 4107

def tnoise(scale, seed, aniso=1.0):
    """Periodic gaussian-filtered noise, ~`scale` px features (x stretched by `aniso`), std 1."""
    r = np.random.default_rng(seed)
    f = np.fft.fft2(r.standard_normal((S, S)))
    k = np.fft.fftfreq(S)
    kk = np.sqrt((k[None, :] * scale * aniso) ** 2 + (k[:, None] * scale) ** 2)
    n = np.real(np.fft.ifft2(f * np.exp(-kk ** 2)))
    return ((n - n.mean()) / n.std()).astype(np.float32)

def grad(h):
    return (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * .5, (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * .5

def pebbles(rng, n):
    """Height + albedo-offset fields for n small rounded pebbles, wrapped so the tile stays seamless."""
    h = np.zeros((S, S), np.float32); tone = np.zeros((S, S), np.float32); cov = np.zeros((S, S), np.float32)
    for _ in range(n):
        cx, cy = rng.uniform(0, S, 2)
        rx = rng.uniform(3, 9) * (1.6 if rng.random() < .15 else 1); ry = rx * rng.uniform(.6, 1.0); th = rng.uniform(0, np.pi)
        t = rng.uniform(-.35, .10)
        R = int(rx) + 3
        xs = (np.arange(int(cx) - R, int(cx) + R + 1)) % S
        ys = (np.arange(int(cy) - R, int(cy) + R + 1)) % S
        dx = np.arange(int(cx) - R, int(cx) + R + 1)[None, :] - cx
        dy = np.arange(int(cy) - R, int(cy) + R + 1)[:, None] - cy
        u = (dx * np.cos(th) + dy * np.sin(th)) / rx; v = (-dx * np.sin(th) + dy * np.cos(th)) / ry
        d = np.sqrt(u * u + v * v)
        m = np.clip((1 - d) * rx * .9, 0, 1)          # anti-aliased edge
        dome = np.sqrt(np.clip(1 - d * d, 0, 1)) * 2.2
        sub = np.ix_(ys, xs)
        h[sub] = np.maximum(h[sub], dome * m)
        tone[sub] = np.where(m > cov[sub], t, tone[sub]); cov[sub] = np.maximum(cov[sub], m)
    return h, tone, cov

def make():
    rng = np.random.default_rng(SEED)
    # --- the bed: wet silt, soft ripple marks left by the shrinking water, a few pebbles -----------
    silt = .55 * tnoise(3, SEED + 1) + .35 * tnoise(9, SEED + 2) + .25 * tnoise(40, SEED + 3)
    ripple_marks = .8 * np.sin((np.arange(S)[:, None] / S * 2 * np.pi * 26) + 2.2 * tnoise(90, SEED + 4)) * .35
    ph, ptone, pcov = pebbles(rng, 60)
    h = silt * .45 + ripple_marks + ph
    gx, gy = grad(h)
    shade = 1 - .32 * (gx * .7 + gy * .7)               # light from the north-west, as on vanilla terrain
    mud = np.array([.285, .215, .170], np.float32)      # vanilla Mud level, darkened ~5% for wetness
    mottle = 1 + .07 * tnoise(70, SEED + 5) + .08 * tnoise(14, SEED + 6) + .05 * tnoise(2, SEED + 11)
    pebble_col = np.array([.35, .31, .27], np.float32)
    bed = mud[None, None] * mottle[..., None]
    pc = (pebble_col[None, None] * (1 + ptone[..., None]))
    bed = bed * (1 - pcov[..., None]) + pc * pcov[..., None]
    bed = bed * shade[..., None]
    # --- the water: a thin, uneven, blue-grey veil; still surface with faint wind streaks ---------
    depth = np.clip(.32 + .045 * tnoise(150, SEED + 7) + .02 * tnoise(30, SEED + 8) - .10 * pcov * (ph > 1.4), .2, .5)
    water = np.array([.33, .40, .44], np.float32)       # WaterShallowRamp level, a touch bluer (thin water takes the sky)
    out = bed * (1 - depth[..., None]) + water[None, None] * depth[..., None]
    streak = tnoise(10, SEED + 9, aniso=16.0)             # long east-west glints (still water, light air)
    glint = np.clip(streak - 1.2, 0, None) * .05 * np.clip(tnoise(120, SEED + 10) * .5 + .6, 0, 1)
    out = out + glint[..., None] * np.array([.85, .95, 1.0], np.float32)
    # a wet sheen on the pebble tops that break the surface
    out = out + (np.clip(-gx - gy, 0, None) * pcov * .10)[..., None]
    # broad sky sheen: soft bands of reflected light that say 'surface' over the bed
    sheen = np.clip(tnoise(110, SEED + 12, aniso=3.0) * .5 + .2, 0, 1) * .045
    out = out + sheen[..., None] * np.array([.8, .9, 1.0], np.float32)
    return np.clip(out, 0, 1)

if __name__ == "__main__":
    a = make()
    p = Path(sys.argv[1]); p.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray((a * 255 + .5).astype(np.uint8), "RGB").convert("RGBA").save(p, optimize=True)
    m = a.reshape(-1, 3).mean(0) * 255
    print(p.name, "mean RGB", m.round(1), "lum std", round(float(a.mean(2).std() * 255), 1))
