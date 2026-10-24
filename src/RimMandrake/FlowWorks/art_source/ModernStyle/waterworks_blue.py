#!/usr/bin/env python3
"""Recolour the Modern pipe-system art from firetruck red to weathered waterworks blue (MODERN_PIPE_REDRAW_FIRETRUCK_RED_RETIRED).

Owner 2026-10-24: "For the modern pipes, the wild firehouse red doesn't look good. Emulate this instead:" + a stock photo of
faded light-blue water mains with bolted flanges and galvanised valves (kept outside the repo; the repo is public).

A recolour, not a redraw: only colour moves, the alpha channel is copied byte for byte, so every piece keeps the geometry the
pipe atlas, joins, seat math and port stubs were fitted to (the 2026-10-23 GPT redraw lost exactly that and hit the round cap).
Per pixel, a weight w (1 inside the red hue band at real saturation, ramping to 0 outside it) blends the original with
  hue  BLUE_H plus a small low-frequency drift,
  sat  s * SAT_K (faded paint),
  val  VAL_0 + VAL_K * v (red reads dark; the photo's blue is light),
then grime: a low-frequency darkening field and sparse paint-wear blotches (paler, greyer), both on recoloured pixels only.
Silver bolts, valves and fittings are not red and are untouched. Deterministic: the noise seed is crc32 of the piece name.

The red originals live in red/ (same relative paths), so the installed art can always be re-derived and the selftest pins
installed == recolour(red original) pixel for pixel.

Usage: waterworks_blue.py OUT_DIR [--src DIR]   writes OUT_DIR/<rel path> for every piece in PIECES (src default: red/)."""
import argparse
import zlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
RED = HERE / "red"
TEX = HERE.parents[1] / "Textures/RimMandrake/FlowWorks"

# Pipe-system pieces that carried the red (census 2026-10-24). Bridges, weirs and river works are not pipes and keep theirs.
PIECES = (
    "Pipe/Modern/UniversalPipe_Atlas.png",
    "Pipe/Modern/UniversalPipe_MenuIcon.png",
    "Joins/Modern/Saddle.png",
    "Joins/Modern/Flange.png",
    "Joins/Modern/Coupler.png",
    "PipePole/Modern/PipeSpan.png",
    "Pump/Modern/RM_LiquidPump.png",
    "Faucet/Modern/RM_PipeFaucet.png",
    "Hose/Styles/Modern/Reel_Deployed.png",
    "Hose/Styles/Modern/Reel_Deployed_north.png",
    "Hose/Styles/Modern/Reel_Deployed_south.png",
    "Hose/Styles/Modern/Reel_PumpHookup.png",
    "Hose/Styles/Modern/Reel_PumpHookup_north.png",
    "Hose/Styles/Modern/Reel_PumpHookup_south.png",
)
SPRINKLER = "Sprinkler/Modern/RM_SprinklerHead.png"  # recoloured inside art_source/Sprinkler/squat_heads.py, after the squat

BLUE_H = 203 / 360   # the photo's main body hue
HUE_DRIFT = 5 / 360  # +- low-frequency hue wander
SAT_K = 0.50
VAL_0, VAL_K = 0.17, 0.80
RED_CORE, RED_EDGE = 16 / 360, 34 / 360   # hue distance from 0: full weight inside CORE, none beyond EDGE
SAT_LO, SAT_HI = 0.18, 0.38               # saturation ramp for the weight (greys and silvers stay out)
GRIME = 0.13          # max darkening of the low-frequency field
WEAR_FRAC = 0.025     # share of recoloured pixels inside worn blotches
WEAR_PALE = 0.35      # how far a worn blotch moves toward weathered grey


def _ramp(x, lo, hi):
    return np.clip((x - lo) / (hi - lo), 0.0, 1.0)


def _field(shape, rng, sigma):
    """A smooth random field in [0, 1], low frequency (sigma in px)."""
    h, w = shape
    n = Image.fromarray((rng.random((h, w)) * 255).astype(np.uint8), "L")
    f = np.asarray(n.filter(ImageFilter.GaussianBlur(sigma)), dtype=float)
    f -= f.min()
    return f / f.max() if f.max() > 0 else f


def red_weight(rgb):
    """Per-pixel weight in [0, 1]: how much a pixel is the Modern red. rgb float array (h, w, 3) in [0, 1]."""
    mx, mn = rgb.max(-1), rgb.min(-1)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    h = _hue(rgb, mx, mn)
    dist = np.minimum(h, 1.0 - h)
    return (1.0 - _ramp(dist, RED_CORE, RED_EDGE)) * _ramp(s, SAT_LO, SAT_HI)


def _hue(rgb, mx, mn):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    d = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, ((g - b) / d) % 6.0, np.where(mx == g, (b - r) / d + 2.0, (r - g) / d + 4.0))
    return np.where(mx - mn > 1e-6, h / 6.0, 0.0)


def _hsv_to_rgb(h, s, v):
    i = np.floor(h * 6.0).astype(int) % 6
    f = h * 6.0 - np.floor(h * 6.0)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    out = np.zeros(h.shape + (3,))
    for k, (a, b, c) in enumerate(((v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q))):
        m = i == k
        out[m, 0], out[m, 1], out[m, 2] = a[m], b[m], c[m]
    return out


def recolour(im, name):
    """Return (RGBA image, info). `name` seeds the noise (use the piece's relative path) so output is reproducible."""
    src = np.asarray(im.convert("RGBA"))
    rgb = src[..., :3].astype(float) / 255.0
    w = red_weight(rgb)
    mx, mn = rgb.max(-1), rgb.min(-1)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    rng = np.random.default_rng(zlib.crc32(name.encode()))
    scale = max(src.shape[:2]) / 256.0
    drift = (_field(w.shape, rng, 9 * scale) - 0.5) * 2 * HUE_DRIFT
    blue = _hsv_to_rgb(np.full(w.shape, BLUE_H) + drift, np.clip(s * SAT_K, 0, 1), np.clip(VAL_0 + VAL_K * mx, 0, 1))
    grime = 1.0 - GRIME * _field(w.shape, rng, 5 * scale) ** 1.5
    blue *= grime[..., None]
    # paint wear: sparse blotches (the top WEAR_FRAC of a mid-frequency field), soft-edged, not salt-and-pepper speckle
    blot = _field(w.shape, rng, 2.2 * scale)
    cut = np.quantile(blot[w > 0.5], 1.0 - WEAR_FRAC) if (w > 0.5).any() else 1.0
    wear = _ramp(blot, cut, cut + 0.06)
    pale = np.array([0.66, 0.66, 0.63])  # chalky grey, slightly warm: dust and primer, not snow
    blue = blue * (1 - WEAR_PALE * wear[..., None]) + pale * (WEAR_PALE * wear[..., None])
    out = rgb * (1 - w[..., None]) + blue * w[..., None]
    res = np.dstack([np.clip(np.round(out * 255), 0, 255).astype(np.uint8), src[..., 3]])
    op = src[..., 3] > 128
    info = {"recoloured_px": int(((w > 0.5) & op).sum()), "opaque_px": int(op.sum())}
    return Image.fromarray(res, "RGBA"), info


def saturated_red_share(im, alpha_min=128):
    """Share of opaque pixels that are saturated red (hue within 20 deg of 0, s > 0.45, v > 0.25). The no-red check."""
    a = np.asarray(im.convert("RGBA")).astype(float) / 255.0
    rgb, op = a[..., :3], a[..., 3] > alpha_min / 255.0
    if not op.any():
        return 0.0
    mx, mn = rgb.max(-1), rgb.min(-1)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    h = _hue(rgb, mx, mn)
    red = (np.minimum(h, 1 - h) < 20 / 360) & (s > 0.45) & (mx > 0.25) & op
    return float(red.sum()) / float(op.sum())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out")
    ap.add_argument("--src", default=str(RED))
    a = ap.parse_args(argv)
    for rel in PIECES:
        im = Image.open(Path(a.src) / rel)
        res, info = recolour(im, rel)
        dst = Path(a.out) / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        res.save(dst)
        print(rel, info, "red before %.3f after %.3f" % (saturated_red_share(im), saturated_red_share(res)))


if __name__ == "__main__":
    main()
