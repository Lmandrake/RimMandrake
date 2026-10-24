#!/usr/bin/env python3
"""The Modern hose reel's wrapped hose as a red woven-canvas firehose on the blue frame (HOSE_REEL_REDRAW_FIREHOSE_ON_THE_DRUM).

Owner 2026-10-24: "red for hose holder is ok (firehose inspired)" and "And I think the blue hose reel needs a firehose-like
hose wrapped around it, not a blue hose". The waterworks-blue recolour (waterworks_blue.py, MODERN_PIPE_REDRAW_FIRETRUCK_RED_
RETIRED) turned the whole reel blue, hose included. This keeps the frame, flanges, pipes and valve exactly as that recolour
made them and redraws only the hose on the drum: a matte red canvas jacket with a fine twill weave.

The drum hose of each texture is a fixed region (MASKS, fitted by eye on 6x crops of the red originals and checked by the
overlay this script writes): the side views' coils lie in a rectangle between the frame uprights; the north/south views'
coils show between the back flange and the front flange, a rectangle minus the front flange's ellipse. Inside it, only
pixels the red original painted red (waterworks_blue.red_weight) move, so the silver hub on Reel_Deployed_south and the
outlines stay. Per pixel: the red original's value v (the coil shading: wraps, grooves, the dark gaps between wraps) is
compressed toward a matte mid (the original was glossy rubber; canvas has no specular), mapped onto a canvas-red ramp, and
multiplied by a twill (threads on a 3 px diagonal) and a per-thread jitter; the region's edge is feathered one pixel
inward. Alpha is the installed alpha byte for byte.

    python3 firehose_reel.py <out_dir> [--overlay]   # <out_dir>/<rel> per piece (+ mask overlays at 4x with --overlay)
"""
import argparse
import zlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import waterworks_blue as wb

REL = "Hose/Styles/Modern/%s.png"
# shapes: ("rect", x0, y0, x1, y1) adds [x0, x1) x [y0, y1); ("dome", x0, x1, cx, cy, a, b, y1) adds the coil stack seen
# end-on, its columns x0..x1 from the top coil's arc (upper half of ellipse cx, cy, a, b) down to y1; ("not_ell", cx, cy, a, b)
# removes the front flange's ellipse. "glint": the stack's white gloss highlights are canvas too (no silver part inside it).
MASKS = {
    "Reel_Deployed": (("rect", 103, 74, 148, 123), ("glint",)),
    "Reel_PumpHookup": (("rect", 81, 56, 164, 139), ("glint",)),
    "Reel_Deployed_north": (("dome", 107, 152, 129.5, 85, 22.5, 18, 100), ("not_ell", 127.5, 136, 52, 43), ("glint",)),
    "Reel_PumpHookup_north": (("dome", 88, 168, 128, 62, 40, 20, 115), ("not_ell", 127.5, 139, 51, 37.5), ("glint",)),
    "Reel_Deployed_south": (("dome", 95, 134, 122, 70, 27, 16, 92), ("not_ell", 127, 122, 50, 41)),
    "Reel_PumpHookup_south": (("dome", 88, 168, 128, 56, 40, 20, 100), ("not_ell", 127.5, 118.5, 50, 39.5), ("glint",)),
}
PIECES = tuple(REL % k for k in MASKS)
# the canvas-red ramp, dark -> light (sRGB 0..1): a faded firehose jacket, darker and duller than the frame's old paint
RAMP = np.array([(0.20, 0.04, 0.035), (0.50, 0.10, 0.08), (0.74, 0.20, 0.15), (0.86, 0.38, 0.30)])
MATTE = (0.10, 0.82)      # v is mapped into this band before the ramp: no white gloss, no black
WEAVE = 0.11              # twill depth (multiplier 1 - WEAVE .. 1)
JITTER = 0.04             # per-thread value jitter


def region(name, shape=(256, 256)):
    """Bool mask of the drum hose region for texture `name` (MASKS key)."""
    h, w = shape
    y, x = np.mgrid[0:h, 0:w] + 0.5
    m = np.zeros(shape, bool)
    for s in MASKS[name]:
        if s[0] == "rect":
            _, x0, y0, x1, y1 = s
            m |= (x >= x0) & (x < x1) & (y >= y0) & (y < y1)
        elif s[0] == "dome":
            _, x0, x1, cx, cy, a, b, y1 = s
            cap = ((x - cx) / a) ** 2 + ((y - cy) / b) ** 2 <= 1.0
            m |= (x >= x0) & (x < x1) & (((y >= cy) & (y < y1)) | cap)
    for s in MASKS[name]:
        if s[0] == "not_ell":
            _, cx, cy, a, b = s
            m &= ((x - cx) / a) ** 2 + ((y - cy) / b) ** 2 > 1.0
    return m


def _ramp(t):
    t = np.clip(t, 0, 1) * (len(RAMP) - 1)
    i = np.minimum(t.astype(int), len(RAMP) - 2)
    f = (t - i)[..., None]
    return RAMP[i] * (1 - f) + RAMP[i + 1] * f


def weave(shape, seed):
    """Multiplier field: a 3 px twill (two of three threads over on each diagonal step) and per-thread jitter."""
    h, w = shape
    y, x = np.mgrid[0:h, 0:w]
    tw = np.where((x + 2 * y) % 3 == 0, 1.0 - WEAVE, np.where((x + 2 * y) % 3 == 1, 1.0 - WEAVE * 0.4, 1.0))
    rng = np.random.default_rng(seed)
    warp = rng.normal(0, JITTER, w)[None, :]
    weft = rng.normal(0, JITTER, h)[:, None]
    return tw * (1 + warp + weft)


def build(name):
    """-> RGBA: the installed blue reel with its drum hose redrawn as firehose. `name` is a MASKS key."""
    rel = REL % name
    red = Image.open(wb.RED / rel).convert("RGBA")
    blue, _ = wb.recolour(red, rel)
    src = np.asarray(red).astype(float) / 255.0
    out = np.asarray(blue).astype(float) / 255.0
    m = region(name, src.shape[:2])
    rgb0 = src[..., :3]
    wt = wb.red_weight(rgb0)
    v = rgb0.max(-1)
    if ("glint",) in MASKS[name]:
        sat = np.where(v > 0, (v - rgb0.min(-1)) / np.maximum(v, 1e-6), 0.0)
        wt = np.maximum(wt, ((sat < 0.3) & (v > 0.8)).astype(float))
    mf = np.pad(m.astype(float), 1, mode="edge")
    mf = sum(mf[1 + dy:1 + dy + m.shape[0], 1 + dx:1 + dx + m.shape[1]] for dy in (-1, 0, 1) for dx in (-1, 0, 1)) / 9.0
    wt = wt * mf * m                  # feathered one pixel inward: no jagged seam where the hose meets a flange rim
    lo, hi = np.percentile(v[m & (src[..., 3] > 0.5)], (2, 98))
    t = MATTE[0] + (MATTE[1] - MATTE[0]) * np.clip((v - lo) / max(hi - lo, 1e-3), 0, 1)
    hose = _ramp(t) * weave(v.shape, zlib.crc32(rel.encode()))[..., None]
    rgb = out[..., :3] * (1 - wt[..., None]) + np.clip(hose, 0, 1) * wt[..., None]
    res = np.dstack([np.clip(np.round(rgb * 255), 0, 255).astype(np.uint8), np.asarray(blue)[..., 3]])
    return Image.fromarray(res, "RGBA")


CANVAS_MIN = 0.6     # share of the drum's hose pixels that must be canvas red
WEAVE_MIN = 0.04     # mean value step between the twill's under and over threads
GLOSS_MAX = 0.005    # share of the drum's hose pixels allowed to be white gloss


def drum_hose_reads_as_firehose(im, name):
    """(ok, canvas, weave, gloss) over the drum hose region of `name` (the pixels the red original painted red there):
    canvas = share that is red (hue within 20 deg of 0, s > 0.45, v > 0.12); weave = 1 - mean v of the twill's under
    threads / mean v of its over threads; gloss = share near-white (s < 0.3, v > 0.8). FAILS on the installed blue
    (no red), on the glossy red original (no weave, white gloss); PASSES on build()."""
    a = np.asarray(im.convert("RGBA")).astype(float) / 255.0
    src = np.asarray(Image.open(wb.RED / (REL % name)).convert("RGBA")).astype(float) / 255.0
    m = region(name, a.shape[:2]) & (a[..., 3] > 0.5) & (wb.red_weight(src[..., :3]) > 0.5)
    if m.sum() < 200:
        return False, 0.0, 0.0, 1.0
    rgb = a[..., :3]
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    hue = wb._hue(rgb, mx, mn)
    red = (np.minimum(hue, 1 - hue) < 20 / 360) & (sat > 0.45) & (mx > 0.12)
    canvas = float(red[m].mean())
    gloss = float(((sat < 0.3) & (mx > 0.8))[m].mean())
    y, x = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    ph = (x + 2 * y) % 3
    over, under = mx[m & (ph == 2)].mean(), mx[m & (ph == 0)].mean()
    weave = float(1.0 - under / max(over, 1e-6))
    return (canvas >= CANVAS_MIN and weave >= WEAVE_MIN and gloss <= GLOSS_MAX), canvas, weave, gloss


def overlay(name, k=4):
    """The red original at k x with the mask outline in yellow: the fit is checked by eye on this."""
    rel = REL % name
    t = Image.open(wb.RED / rel).convert("RGBA")
    bg = Image.new("RGBA", t.size, (60, 60, 60, 255))
    bg.alpha_composite(t)
    a = np.asarray(bg.resize((t.size[0] * k, t.size[1] * k), Image.NEAREST)).copy()
    m = np.repeat(np.repeat(region(name, (t.size[1], t.size[0])), k, 0), k, 1)
    edge = m & ~(np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1))
    a[edge] = (255, 255, 0, 255)
    im = Image.fromarray(a, "RGBA")
    ImageDraw.Draw(im).text((4, 4), name, fill=(255, 255, 255, 255))
    return im


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out")
    ap.add_argument("--overlay", action="store_true")
    a = ap.parse_args(argv)
    for name in MASKS:
        dst = Path(a.out) / (REL % name)
        dst.parent.mkdir(parents=True, exist_ok=True)
        build(name).save(dst)
        if a.overlay:
            overlay(name).save(Path(a.out) / ("overlay_%s.png" % name))
        print(dst)


if __name__ == "__main__":
    main()
