#!/usr/bin/env python3
"""aiwha_composite.py — deterministic wing-first composite for RSW_Aiwha (AIWHA_REDRAW_WINGS_STILL_TOO_SHORT).

Owner card 2026-10-14: "Redraw with a wing-first prompt", after four whole-animal renders
(donorport_aiwha_v1..v4) all failed the canon check's wingspan line ("span many times the body
length": the grader measured 1.2-3 body lengths and asked for five). A generator will not hold
that ratio, so the WINGS and the BODY are generated as separate artpipe pieces and this script
fixes the ratio by arithmetic:

  1. crop each piece to its alpha bbox (alpha > ALPHA_T);
  2. scale the wing pair so tip-to-tip = canvas width - 2*margin (or the height limit);
  3. scale the body so its snout-to-fluke length = wingspan / ratio (default 6.0);
  4. put the body's SHOULDER (x = shoulder_frac of the body bbox from the tail end, y = alpha
     midpoint of that column) on the wing ROOT (the wing pair's centre column, alpha midpoint);
     the body is drawn over the wings;
  5. centre the union vertically in the canvas.

The body piece faces RIGHT (east) for --facing east; for a top-down piece (north/south) the
body runs vertically and "length" is its bbox height, the shoulder measured from the tail end
along y (head at top for north is NOT assumed: pass --head up|down).

    python3 aiwha_composite.py --wings W.png --body B.png --out east.png [--canvas 768x384]
           [--ratio 6] [--margin 8] [--shoulder 0.6] [--facing east|north|south] [--head up|down]
           [--wing-squash 0.6] [--match-hue]

--wing-squash narrows the wing chord (the generated pair came out broader than canon's narrow blades);
--match-hue rotates the wing piece's mean hue onto the body piece's so two generations read as one hide.

Prints the measured geometry (span, body length, ratio) as one JSON line.
Selftest: selftest_aiwha_composite.py.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image

ALPHA_T = 16


def crop_alpha(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    box = im.getchannel("A").point(lambda a: 255 if a > ALPHA_T else 0).getbbox()
    if not box:
        raise ValueError("piece has no opaque pixels")
    return im.crop(box)


def _mid_alpha(im: Image.Image, x: int | None = None, y: int | None = None) -> float:
    """Midpoint of the opaque run along a column (x) or row (y)."""
    a = im.getchannel("A")
    w, h = im.size
    if x is not None:
        idx = [j for j in range(h) if a.getpixel((x, j)) > ALPHA_T]
    else:
        idx = [i for i in range(w) if a.getpixel((i, y)) > ALPHA_T]
    if not idx:
        raise ValueError("no opaque pixels on the sampled line")
    return (idx[0] + idx[-1]) / 2.0


def _scale(im: Image.Image, f: float) -> Image.Image:
    return im.resize((max(1, round(im.width * f)), max(1, round(im.height * f))), Image.LANCZOS)


def mean_hue(im: Image.Image, min_sat: int = 40) -> float | None:
    """Circular mean hue (0-255 PIL scale) of opaque, saturated pixels; None if there are none.
    The saturation floor keeps the cream underside (near-grey, unstable hue) out of the mean."""
    import math
    hsv = im.convert("RGB").convert("HSV")
    a = im.getchannel("A")
    sx = sy = 0.0
    for (h, s, _v), al in zip(hsv.getdata(), a.getdata()):
        if al > 128 and s >= min_sat:
            t = h / 256.0 * 2 * math.pi
            sx += math.cos(t) * s
            sy += math.sin(t) * s
    if sx == 0 and sy == 0:
        return None
    return (math.atan2(sy, sx) / (2 * math.pi) * 256.0) % 256.0


def shift_hue(im: Image.Image, delta: float, lo: int = 20, hi: int = 50) -> Image.Image:
    """Rotate hue by `delta`, weighted by saturation: pixels below `lo` keep their colour (the cream
    underside would otherwise turn pink), above `hi` take the full shift, linear ramp between."""
    a = im.getchannel("A")
    rgb = im.convert("RGB")
    h, s, v = rgb.convert("HSV").split()
    d = round(delta) % 256
    shifted = Image.merge("HSV", (h.point(lambda x: (x + d) % 256), s, v)).convert("RGB")
    mask = s.point(lambda x: 0 if x <= lo else 255 if x >= hi else round(255 * (x - lo) / (hi - lo)))
    out = Image.composite(shifted, rgb, mask).convert("RGBA")
    out.putalpha(a)
    return out


def composite(wings: Image.Image, body: Image.Image, canvas=(768, 384), ratio=6.0, margin=8,
              shoulder=0.6, facing="east", head="up", wing_squash=1.0,
              match_hue=False) -> tuple[Image.Image, dict]:
    W, H = canvas
    wg = crop_alpha(wings)
    bd = crop_alpha(body)
    hue_delta = 0.0
    if match_hue:
        hb, hw = mean_hue(bd), mean_hue(wg)
        if hb is not None and hw is not None:
            hue_delta = ((hb - hw + 128) % 256) - 128
            wg = shift_hue(wg, hue_delta)
    if wing_squash != 1.0:  # narrow the wing chord (vertical extent) without touching the span
        wg = wg.resize((wg.width, max(1, round(wg.height * wing_squash))), Image.LANCZOS)
    f = min((W - 2 * margin) / wg.width, (H - 2 * margin) / wg.height)
    wg = _scale(wg, f)
    span = wg.width
    vertical = facing in ("north", "south")
    body_len_src = bd.height if vertical else bd.width
    bd = _scale(bd, (span / ratio) / body_len_src)
    root_x = wg.width // 2
    root_y = _mid_alpha(wg, x=root_x)
    if vertical:
        sy = round(bd.height * ((1 - shoulder) if head == "up" else shoulder))  # measured from the tail end
        sy = min(max(sy, 0), bd.height - 1)
        sh_y, sh_x = sy, _mid_alpha(bd, y=sy)
    else:
        sx = min(max(round(bd.width * shoulder), 0), bd.width - 1)  # tail at left, head at right
        sh_x, sh_y = sx, _mid_alpha(bd, x=sx)
    # layout in wing coords, then centre the union
    bx, by = round(root_x - sh_x), round(root_y - sh_y)
    x0, y0 = min(0, bx), min(0, by)
    x1, y1 = max(wg.width, bx + bd.width), max(wg.height, by + bd.height)
    if x1 - x0 > W or y1 - y0 > H:
        raise ValueError(f"composite {x1 - x0}x{y1 - y0} does not fit canvas {W}x{H}")
    ox = (W - (x1 - x0)) // 2 - x0
    oy = (H - (y1 - y0)) // 2 - y0
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(wg, (ox, oy))
    out.alpha_composite(bd, (ox + bx, oy + by))
    geo = {"canvas": [W, H], "wingspan_px": span, "body_len_px": bd.height if vertical else bd.width,
           "ratio": round(span / (bd.height if vertical else bd.width), 3),
           "wing_box": [ox, oy, ox + wg.width, oy + wg.height],
           "body_box": [ox + bx, oy + by, ox + bx + bd.width, oy + by + bd.height],
           "root": [ox + root_x, oy + root_y], "shoulder": [ox + bx + sh_x, oy + by + sh_y], "facing": facing,
           "wing_squash": wing_squash, "wing_hue_shift": round(hue_delta, 1)}
    return out, geo


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--wings", type=Path, required=True)
    ap.add_argument("--body", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--canvas", default="768x384")
    ap.add_argument("--ratio", type=float, default=6.0)
    ap.add_argument("--margin", type=int, default=8)
    ap.add_argument("--shoulder", type=float, default=0.6)
    ap.add_argument("--facing", choices=("east", "north", "south"), default="east")
    ap.add_argument("--head", choices=("up", "down"), default="up")
    ap.add_argument("--wing-squash", type=float, default=1.0, help="scale the wing piece's height (chord) by this")
    ap.add_argument("--match-hue", action="store_true", help="rotate the wings' mean hue onto the body's")
    a = ap.parse_args(argv)
    W, H = (int(v) for v in a.canvas.lower().split("x"))
    out, geo = composite(Image.open(a.wings), Image.open(a.body), (W, H), a.ratio, a.margin,
                         a.shoulder, a.facing, a.head, a.wing_squash, a.match_hue)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    out.save(a.out)
    print(json.dumps(geo))
    return 0


if __name__ == "__main__":
    sys.exit(main())
