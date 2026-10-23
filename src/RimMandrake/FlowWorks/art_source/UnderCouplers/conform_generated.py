#!/usr/bin/env python3
"""Conform GENERATED under-coupler masters (Codex $imagegen, 576x1280 collar / 1536x512 pipe) to the exact canvases
Machinery/UnderCouplerGeometry.cs draws: UnderCollar 36x80, UnderPipe 32x56 (+u = into the fixture; the left edge is the port face).

  python3 conform_generated.py <Look> <collar_master.png> <pipe_master.png> <outdir> [--pipe profile|textured]

Collar: crop to the solid-alpha box (alpha >= 32), downscale premultiplied (LANCZOS) to 36x80, clear the faint fringe.
Pipe:   the quad is STRETCHED along u to any length (0.1..~1.5 cell), so
  profile   (default) averages the central 60% of the master along x into ONE cross-section, resampled to 56 rows and
            repeated across all 32 columns: identical at every length (GPT review 2026-10-23 recommendation).
  textured  keeps the master's along-axis paint: a central crop of world aspect 2.29:1 (a 0.5-cell pipe run, 0.21875 wide)
            squeezed into 32x56, so it reads undistorted at 0.5 cell and smears/compresses at other lengths.
Writes <outdir>/<Look>/UnderCollar.png and UnderPipe.png. Never writes into Textures/ (install goes through the art ledger).
"""
import os
import sys

import numpy as np
from PIL import Image

COLLAR, PIPE = (36, 80), (32, 56)


def _solid_box(im, thr=32):
    a = np.array(im)[..., 3]
    ys, xs = np.where(a >= thr)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def _down(im, size):
    """Premultiplied-alpha downscale (no dark halo), then fringe pixels (alpha 1..31) cleared."""
    out = np.array(im.convert("RGBa").resize(size, Image.LANCZOS).convert("RGBA"))
    a = out[..., 3]
    out[(a > 0) & (a < 32)] = 0
    if size[0] > 1:                       # the cross-axis edge rows antialiased at half alpha, as the procedural sprites were
        out[0, :, 3] //= 2
        out[-1, :, 3] //= 2
    return Image.fromarray(out, "RGBA")


def collar(path):
    im = Image.open(path).convert("RGBA")
    return _down(im.crop(_solid_box(im)), COLLAR)


def pipe(path, mode):
    im = Image.open(path).convert("RGBA")
    im = im.crop(_solid_box(im))
    w, h = im.size
    if mode == "textured":
        cw = min(w, int(round(h * 0.5 / 0.21875)))
        x0 = (w - cw) // 2
        return _down(im.crop((x0, 0, x0 + cw, h)), PIPE)
    x0, x1 = int(w * 0.2), int(w * 0.8)
    a = np.array(im, float)[:, x0:x1]
    al = a[..., 3:4] / 255.0
    rgb = (a[..., :3] * al).sum(1) / np.maximum(al.sum(1), 1e-6)     # premultiplied column average, per row
    alpha = a[..., 3].mean(1)
    prof = np.concatenate([rgb, alpha[:, None]], 1)                   # h x 4
    col = Image.fromarray(np.clip(prof[:, None, :], 0, 255).astype(np.uint8), "RGBA")   # 1 x h
    col = _down(col, (1, PIPE[1]))
    col = np.array(col.resize(PIPE, Image.NEAREST))
    col[0, :, 3] //= 2
    col[-1, :, 3] //= 2
    return Image.fromarray(col, "RGBA")


def main(argv):
    mode = "profile"
    if "--pipe" in argv:
        i = argv.index("--pipe")
        mode = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if len(argv) != 5 or mode not in ("profile", "textured"):
        print(__doc__)
        return 2
    look, cm, pm, outdir = argv[1:]
    d = os.path.join(outdir, look)
    os.makedirs(d, exist_ok=True)
    collar(cm).save(os.path.join(d, "UnderCollar.png"))
    pipe(pm, mode).save(os.path.join(d, "UnderPipe.png"))
    print("wrote", d, mode)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
