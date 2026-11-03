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

Masked pass (MODERN_FLANGES_POLISH_DARKER_THAN_THE_BODY, from the art judge on the first recolour): the owner's reference has
flange rings in a deeper, darker blue than the pipe body and keeps valve handwheels galvanised grey. PART_MASKS gives per piece
hand-fitted shapes in source px (fitted by eye on 6x crops, checked with --overlay): under a "flange" mask the recoloured blue
is darkened (FLANGE_VAL) and deepened (FLANGE_SAT), gated by the red weight so silver bolts inside do not move; under a "valve"
mask the final pixel becomes galvanised grey (its luminance, a faint cool tint), so the red's pinkish specular dots go grey
too and silver, already grey, stays put. Both masks are feathered one pixel.
Pieces without masks (the pipe atlas, menu icon, saddle, span, the sprinkler head) are recoloured exactly as before. The pump's
masks stay on its four end flanges, outside the round core the sprinkler head is cut from.

The red originals live in red/ (same relative paths), so the installed art can always be re-derived and the selftest pins
installed == recolour(red original) pixel for pixel.

Usage: waterworks_blue.py OUT_DIR [--src DIR] [--only REL ...] [--overlay]
  writes OUT_DIR/<rel path> for every piece in PIECES (src default: red/); --overlay adds mask outlines at 4x.
  The installed atlas has geometry edits on top of this recolour and the reels get their firehose from firehose_reel.py:
  install from --only, never by copying the whole OUT_DIR."""
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
SPRINKLER = "Sprinkler/Modern/RM_SprinklerHead.png"  # historical: since SPRINKLER_HEAD_REDRAW_SEEN_FROM_ABOVE the head is cut from the Modern pump (art_source/Sprinkler/top_heads.py), already blue

BLUE_H = 203 / 360   # the photo's main body hue
HUE_DRIFT = 5 / 360  # +- low-frequency hue wander
SAT_K = 0.50
VAL_0, VAL_K = 0.17, 0.80
RED_CORE, RED_EDGE = 16 / 360, 34 / 360   # hue distance from 0: full weight inside CORE, none beyond EDGE
SAT_LO, SAT_HI = 0.18, 0.38               # saturation ramp for the weight (greys and silvers stay out)
GRIME = 0.13          # max darkening of the low-frequency field
WEAR_FRAC = 0.025     # share of recoloured pixels inside worn blotches
WEAR_PALE = 0.35      # how far a worn blotch moves toward weathered grey
FLANGE_VAL = 0.62     # flange rings: value multiplier (darker than the body)
FLANGE_SAT = 1.35     # flange rings: chroma multiplier (deeper blue, not a grey shadow)
VALVE_TINT = (0.97, 1.0, 1.04)   # galvanised grey: luminance with a faint cool cast

# Per-piece part masks, source px. ("rect", x0, y0, x1, y1) is [x0, x1) x [y0, y1); ("ell", cx, cy, rx, ry) an ellipse.
_REEL = "Hose/Styles/Modern/%s.png"
PART_MASKS = {
    "Joins/Modern/Flange.png": {"flange": [("rect", 0, 0, 128, 128)]},    # the whole piece is a flange ring
    "Joins/Modern/Coupler.png": {"flange": [("rect", 0, 0, 128, 128)]},   # two mated flange rings
    "Pump/Modern/RM_LiquidPump.png": {"flange": [("rect", 178, 26, 338, 80), ("rect", 178, 413, 338, 482),
                                                 ("rect", 10, 176, 76, 336), ("rect", 435, 176, 502, 336)]},
    "Faucet/Modern/RM_PipeFaucet.png": {"valve": [("rect", 94, 68, 164, 113)]},   # the cross handle (arm tips reach the corners)
    _REEL % "Reel_Deployed": {"valve": [("ell", 205, 76, 16, 10)]},
    _REEL % "Reel_Deployed_north": {"valve": [("ell", 127.5, 128, 17, 10)]},
    _REEL % "Reel_Deployed_south": {"valve": [("ell", 127, 16, 12, 5.5)]},
    _REEL % "Reel_PumpHookup": {"valve": [("ell", 202.5, 77.5, 20, 11)]},
    _REEL % "Reel_PumpHookup_north": {"valve": [("ell", 126.5, 130, 18, 11)]},
    _REEL % "Reel_PumpHookup_south": {"valve": [("ell", 125.7, 18.3, 13, 6)]},
}


def _ramp(x, lo, hi):
    return np.clip((x - lo) / (hi - lo), 0.0, 1.0)


def _field(shape, rng, sigma):
    """A smooth random field in [0, 1], low frequency (sigma in px)."""
    h, w = shape
    n = Image.fromarray((rng.random((h, w)) * 255).astype(np.uint8), "L")
    f = np.asarray(n.filter(ImageFilter.GaussianBlur(sigma)), dtype=float)
    f -= f.min()
    return f / f.max() if f.max() > 0 else f


def part_mask(name, kind, shape):
    """Hard boolean mask of PART_MASKS[name][kind] on an (h, w) canvas (all False when the piece has none)."""
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    m = np.zeros((h, w), bool)
    for sh in PART_MASKS.get(name, {}).get(kind, ()):
        if sh[0] == "rect":
            x0, y0, x1, y1 = sh[1:]
            m |= (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)
        else:
            cx, cy, rx, ry = sh[1:]
            m |= ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0
    return m


def _soft(m):
    """A boolean mask feathered one pixel (3x3 box) into [0, 1]."""
    if not m.any():
        return np.zeros(m.shape)
    f = Image.fromarray(m.astype(np.uint8) * 255, "L").filter(ImageFilter.BoxBlur(1))
    return np.asarray(f, dtype=float) / 255.0


def _luma(rgb):
    return rgb @ np.array([0.299, 0.587, 0.114])


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
    fl = _soft(part_mask(name, "flange", w.shape))[..., None]
    if fl.any():
        g = blue.mean(-1, keepdims=True)
        deep = np.clip((g + (blue - g) * FLANGE_SAT) * FLANGE_VAL, 0, 1)
        blue = blue * (1 - fl) + deep * fl
    out = rgb * (1 - w[..., None]) + blue * w[..., None]
    va = _soft(part_mask(name, "valve", w.shape))[..., None]
    if va.any():   # the whole valve, not only its red-weighted part: the red's pink specular dots must go grey too
        galv = np.clip(_luma(out)[..., None] * np.array(VALVE_TINT), 0, 1)
        out = out * (1 - va) + galv * va
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
    ap.add_argument("--only", nargs="*", help="relative paths to write (default: every piece)")
    ap.add_argument("--overlay", action="store_true")
    a = ap.parse_args(argv)
    for rel in a.only or PIECES:
        im = Image.open(Path(a.src) / rel)
        res, info = recolour(im, rel)
        dst = Path(a.out) / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        res.save(dst)
        if a.overlay and rel in PART_MASKS:
            k = 4
            bg = Image.new("RGBA", res.size, (60, 60, 60, 255))
            bg.alpha_composite(res)
            big = np.asarray(bg.resize((res.size[0] * k, res.size[1] * k), Image.NEAREST)).copy()
            for kind, col in (("flange", (255, 255, 0, 255)), ("valve", (255, 0, 255, 255))):
                m = np.repeat(np.repeat(part_mask(rel, kind, res.size[::-1]), k, 0), k, 1)
                edge = m & ~(np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1))
                big[edge] = col
            Image.fromarray(big, "RGBA").save(Path(a.out) / ("overlay_" + rel.replace("/", "_")))
        print(rel, info, "red before %.3f after %.3f" % (saturated_red_share(im), saturated_red_share(res)))


if __name__ == "__main__":
    main()
