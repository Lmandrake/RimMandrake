"""Turns a flat drawing into paint on a wall: what a hand and a dry brush do to it, baked into the mark's texture.

Removes the dark outline that makes a sticker, breaks the edge, drags dry-brush streaks through the fill, varies the
pressure, adds overspray, and lets runs fall straight down. Colours are pulled into the game's dull pigments so a mark
belongs to the same world as the wall. Deterministic per `seed`.

usage: paintify.py in.png out.png --mode brush|spray|paste|scratch [--wear 0..1] [--seed N] [--size W H]
"""
import argparse

import numpy as np
from PIL import Image, ImageFilter

# Pigments a colony could actually mix: earth, soot, lime, rust, oxide, dull blue. Mid-value, never neon.
PIGMENTS = np.array([
    (146, 52, 38),   # rust red
    (108, 34, 30),   # oxblood
    (170, 118, 52),  # ochre
    (196, 188, 164), # lime wash
    (232, 226, 206), # chalk
    (30, 28, 28),    # soot
    (84, 104, 66),   # oxide green
    (66, 88, 108),   # dull blue
    (108, 72, 110),  # dull violet (lichen dye)
    (172, 92, 44),   # burnt orange
    (140, 136, 124), # ash
], float)


def blur(a, r):
    return np.asarray(Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(float) / 255


def noise(shape, scale, rng):
    """Smooth value noise in 0..1 at feature size `scale` (x, y) pixels."""
    h, w = shape
    sx, sy = (scale, scale) if np.isscalar(scale) else scale
    g = rng.random((max(2, int(h / sy) + 2), max(2, int(w / sx) + 2)))
    im = Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(im).astype(float) / 255


def stretch(a, lo=0.02, hi=0.98):
    l, h = np.quantile(a, lo), np.quantile(a, hi)
    return np.clip((a - l) / max(1e-6, h - l), 0, 1)


def fractal(shape, scale, rng, octaves=3):
    out = np.zeros(shape)
    amp = 1.0
    for i in range(octaves):
        s = (scale[0] / 2 ** i, scale[1] / 2 ** i) if not np.isscalar(scale) else scale / 2 ** i
        out += amp * noise(shape, s, rng)
        amp *= 0.55
    return stretch(out)


def strip_outline(rgb, alpha, px):
    """A dark rim that hugs the shape's edge all the way round is what reads as a sticker: eat it. Interior darks stay."""
    solid = alpha > 0.5
    inner = np.asarray(Image.fromarray((solid * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(2 * px + 1))) > 127
    rim = solid & ~inner
    l = rgb.mean(2)
    if rim.sum() == 0:
        return alpha
    fill = np.median(l[inner]) if inner.sum() else l[solid].mean()
    rimdark = np.median(l[rim])
    if rimdark < 0.55 * fill or rimdark < 50:
        return np.where(rim & (l < max(fill * 0.75, 60)), 0, alpha)
    return alpha


def to_pigment(rgb, amount=0.75):
    """Each pixel moves toward the nearest pigment and loses saturation: sits in the game's palette, keeps its identity."""
    flat = rgb.reshape(-1, 3)
    d = ((flat[:, None, :] - PIGMENTS[None, :, :]) ** 2).sum(2)
    near = PIGMENTS[d.argmin(1)].reshape(rgb.shape)
    grey = rgb.mean(2, keepdims=True)
    muted = grey + (rgb - grey) * 0.62
    return muted * (1 - amount) + near * amount


def add_runs(rgb, alpha, rng, count, maxlen, width):
    """Runs start from wet paint at the shape's lower edges and fall straight down the image, thinning out."""
    h, w = alpha.shape
    wet = alpha > 0.55
    below = np.zeros_like(wet)
    below[:-3, :] = wet[:-3, :] & ~wet[3:, :]
    ys, xs = np.nonzero(below)
    if len(xs) == 0:
        return rgb, alpha
    rgb, alpha = rgb.copy(), alpha.copy()
    for _ in range(count):
        i = rng.integers(len(xs))
        x, y = xs[i], ys[i]
        n = int(rng.uniform(0.25, 1.0) ** 1.6 * maxlen)
        wd = rng.uniform(width * 0.5, width)
        c = rgb[max(0, y - 2), x].copy()
        for j in range(n):
            f = j / max(1, n)
            yy = y + j
            if yy >= h:
                break
            hw = wd * (1 - 0.65 * f) / 2
            x0, x1 = int(round(x - hw)), int(round(x + hw)) + 1
            x0, x1 = max(0, x0), min(w, x1)
            a = 0.88 * (1 - f ** 2.2) + 0.12
            alpha[yy, x0:x1] = np.maximum(alpha[yy, x0:x1], a)
            rgb[yy, x0:x1] = np.where(alpha[yy, x0:x1, None] <= a, c, rgb[yy, x0:x1])
        # bead at the end of the run
        yy = min(h - 1, y + n)
        r = max(1, int(wd * 0.55))
        alpha[max(0, yy - r):yy + r, max(0, x - r):x + r + 1] = np.maximum(alpha[max(0, yy - r):yy + r, max(0, x - r):x + r + 1], 0.7)
        rgb[max(0, yy - r):yy + r, max(0, x - r):x + r + 1] = c
    return rgb, alpha


def paintify(img, mode="brush", wear=0.3, seed=1, size=None, pigment=0.7, runs=None):
    rng = np.random.default_rng(seed)
    if size:
        img = img.resize(size, Image.LANCZOS)
    a = np.asarray(img.convert("RGBA")).astype(float)
    rgb, alpha = a[..., :3].copy(), a[..., 3] / 255
    h, w = alpha.shape
    scale = w / 512  # features are authored for 256 px per wall cell at a 2-cell width

    if mode != "scratch":
        alpha = strip_outline(rgb, alpha, max(1, int(5 * scale)))
        # Colour out of the holes so soft edges never pull in the source's dark matte.
        filled = rgb * alpha[..., None]
        wsum = blur(alpha, 6 * scale) + 1e-3
        spread = np.dstack([blur(filled[..., i] / 255, 6 * scale) for i in range(3)]) * 255 / wsum[..., None]
        rgb = np.where(alpha[..., None] > 0.5, rgb, np.clip(spread, 0, 255))
        rgb = to_pigment(rgb, pigment)

    if mode == "brush":
        # Edge: displaced threshold makes a torn, bristly boundary, never a cut.
        edge = fractal((h, w), (20 * scale, 7 * scale), rng)
        soft = blur(alpha, 4 * scale)
        body = np.clip((soft - (0.34 + 0.34 * edge)) / 0.10, 0, 1)
        # Dry-brush: long streaks along the stroke (the brush runs level on a wall). Streaks deepen where the brush lifts.
        streak = fractal((h, w), (150 * scale, 2.6 * scale), rng, 3)
        load = fractal((h, w), (90 * scale, 60 * scale), rng, 2)
        dry = np.clip((streak - (0.55 - 0.55 * load - 0.2 * (1 - wear))) / 0.14, 0, 1)
        speck = rng.random((h, w))
        pressure = 0.72 + 0.28 * fractal((h, w), (70 * scale, 40 * scale), rng, 2)
        alpha = body * (0.25 + 0.75 * dry) * pressure * (speck > 0.04 + 0.1 * wear)
    elif mode == "spray":
        # A can: soft edge falling off into fine dots, denser at the core.
        soft = blur(alpha, 3.2 * scale)
        halo = blur(alpha, 13 * scale)
        dots = rng.random((h, w))
        core = np.clip((soft - 0.42) / 0.3, 0, 1)
        fall = np.clip(halo * 1.15, 0, 1) ** 2
        overspray = (dots < fall * 0.34).astype(float) * 0.55
        hiss = 0.8 + 0.2 * fractal((h, w), (50 * scale, 50 * scale), rng, 2)
        alpha = np.maximum(core * hiss, overspray)
        rgb_blend = blur(alpha, 1)
        alpha = alpha * 0.55 + rgb_blend * 0.45
    elif mode == "paste":
        # Paper on a wall: a torn edge, wrinkles, rips that show the wall, and wet paste staining the fringe.
        edge = fractal((h, w), (18 * scale, 18 * scale), rng)
        soft = blur(alpha, 3 * scale)
        alpha = np.clip((soft - (0.30 + 0.45 * edge)) / 0.05, 0, 1)
        wrinkle = fractal((h, w), (70 * scale, 8 * scale), rng, 3)
        rgb = rgb * (0.78 + 0.34 * wrinkle[..., None])
        rip = fractal((h, w), (55 * scale, 80 * scale), rng, 3)
        alpha = alpha * (rip > 0.14 + 0.32 * wear)
        fade = 0.8 + 0.2 * fractal((h, w), (120 * scale, 120 * scale), rng, 2)
        alpha = alpha * fade
    elif mode == "scratch":
        # Gouged into the surface: no paint, so no runs. Broken lines only.
        streak = fractal((h, w), (24 * scale, 24 * scale), rng, 2)
        alpha = alpha * np.clip((streak - 0.2) / 0.25, 0, 1)
    else:
        raise ValueError(mode)

    # Weather comes last and takes whole patches, then fades what stayed.
    if wear > 0:
        patch = fractal((h, w), (110 * scale, 70 * scale), rng, 3)
        alpha = alpha * np.clip((patch - wear * 0.42) / 0.16, 0, 1)
        alpha = alpha * (1 - 0.3 * wear * (1 - fractal((h, w), (40 * scale, 16 * scale), rng, 2)))

    if mode in ("brush", "spray"):
        count = int((runs if runs is not None else 7) * (w / max(h, 1)))
        rgb, alpha = add_runs(rgb, alpha, rng, count, int(h * 0.42), 7 * scale)

    rgb = rgb * (0.94 + 0.08 * fractal((h, w), (5, 5), rng, 1)[..., None])
    out = np.dstack((np.clip(rgb, 0, 255), np.clip(alpha, 0, 1) * 255)).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--mode", default="brush")
    ap.add_argument("--wear", type=float, default=0.3)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--size", type=int, nargs=2)
    args = ap.parse_args()
    paintify(Image.open(args.src), args.mode, args.wear, args.seed, tuple(args.size) if args.size else None).save(args.dst)
