#!/usr/bin/env python3
"""The weir's animated white water (weir review 2026-10-23, WEIR_LOOK_REDESIGN_WHITEWATER_FROZEN_SOLID; owner: "Static
white water that doesn't match anything. (needs to be an animated effect)").

Procedural, deterministic, no model: 12 frames of tumbling foam, crest at the TOP (the wall), falling SOUTH (down the
image). RM_Building_BankWeir.DrawWhiteWater turns the plane to the real downstream side and stretches it to the flow's
reach; the material's alpha scales it to the lane (RM_RiverMath.WeirFoam).

Seamless in TIME: every noise layer is periodic along the fall axis and moves a whole number of its periods over the
loop, so frame 11 -> frame 0 does not jump. Seamless ACROSS: periodic along the wall, so joined sections read as one
sheet of white water. Translucent off-white so the map's own water colour shows through (every water on the planet).

    python3 whitewater_frames.py [--out DIR]   (default: the mod's Textures/RimMandrake/FlowWorks/Weir/WhiteWater)
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE.parents[1] / "Textures" / "RimMandrake" / "FlowWorks" / "Weir" / "WhiteWater"
SIZE = 128
FRAMES = 12


def spectral_noise(seed, beta, lo, hi, stretch=1.0):
    """Tileable noise: white noise filtered in the frequency domain (1/f^beta between radii lo..hi), so it is periodic in
    BOTH axes by construction. stretch > 1 elongates features down the fall (v) axis. Normalised 0..1."""
    rng = np.random.default_rng(seed)
    w = rng.normal(size=(SIZE, SIZE))
    fy = np.fft.fftfreq(SIZE)[:, None] * SIZE * stretch
    fx = np.fft.fftfreq(SIZE)[None, :] * SIZE
    r = np.sqrt(fx * fx + fy * fy)
    filt = np.where((r >= lo) & (r <= hi), 1.0 / np.maximum(r, 1.0) ** beta, 0.0)
    f = np.real(np.fft.ifft2(np.fft.fft2(w) * filt))
    return (f - f.min()) / (f.max() - f.min())


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def frames():
    # three layers that each move a WHOLE number of periods over the loop (1, 2 and 3 textures): seamless in time, and
    # because they slide past each other at different speeds the foam churns instead of riding a conveyor belt
    mass = spectral_noise(11, 1.2, 2, 14, stretch=0.8)
    boil = spectral_noise(23, 0.9, 6, 30)
    fleck = spectral_noise(31, 0.6, 10, 48, stretch=2.5)
    v = (np.arange(SIZE) / (SIZE - 1))[:, None]
    # where foam stands: almost all of it under the crest, thinning to scattered flecks and streaks by the far edge
    thr = 0.30 + 0.42 * smoothstep(0.0, 1.0, v)
    haze = 0.30 * np.exp(-v / 0.35)                  # aerated water: a milky veil strongest at the foot of the fall
    lipn = spectral_noise(41, 0.8, 3, 20)[0]         # one row: the lip's tongues along the wall (periodic across)
    out = []
    for k in range(FRAMES):
        m = np.roll(mass, int(round(k * SIZE / FRAMES)), axis=0)
        b = np.roll(boil, int(round(k * 2 * SIZE / FRAMES)), axis=0)
        fl = np.roll(fleck, int(round(k * 3 * SIZE / FRAMES)), axis=0)
        dens = 0.5 * m + 0.3 * b + 0.2 * fl
        # the sheet landing: a white lip under the crest whose depth wavers along the wall and over time
        depth = 0.05 + 0.09 * np.roll(lipn, int(round(k * SIZE / FRAMES)))[None, :]
        curtain = smoothstep(depth, depth * 0.4, v)
        foam = smoothstep(thr - 0.04, thr + 0.06, dens)
        crown = smoothstep(thr + 0.06, thr + 0.2, dens)
        a = np.maximum(np.maximum(foam * 0.92, haze), curtain * 0.95)
        a *= smoothstep(1.0, 0.85, v)                # soft far edge: no hard line downstream
        lit = np.maximum(crown, curtain)
        shade = np.array([214, 222, 220])            # foam in its own shadow, a touch cool
        bright = np.array([251, 252, 248])
        rgb = shade * (1 - lit[..., None]) + bright * lit[..., None]
        out.append((rgb, np.clip(a, 0, 1)))
    return out


def side_fade(a, low, high):
    """An end of the white water (no foam drawn beside it along the wall): fade the outer quarter, unevenly, so a lone
    section or the last one of a run ends in broken foam rather than a straight edge. low = image-left (u=0) side."""
    u = (np.arange(SIZE) / (SIZE - 1))[None, :]
    wob = 0.06 * spectral_noise(53, 0.8, 2, 12)
    m = np.ones_like(a)
    if low:
        m = m * smoothstep(0.02, 0.30, u + wob)
    if high:
        m = m * smoothstep(0.98, 0.70, u - wob)
    return a * m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    n = 0
    for i, (rgb, a) in enumerate(frames()):
        # "" = both sides continue (tileable along the wall); _a = image-left end; _b = image-right end; _ab = a lone section
        for suffix, low, high in (("", False, False), ("_a", True, False), ("_b", False, True), ("_ab", True, True)):
            img = np.dstack([rgb, side_fade(a, low, high) * 255]).astype(np.uint8)
            Image.fromarray(img, "RGBA").save(args.out / f"RM_WeirWhiteWater_{i:02d}{suffix}.png")
            n += 1
    print(f"wrote {n} textures ({FRAMES} frames x 4 end variants) to {args.out}")


if __name__ == "__main__":
    main()
