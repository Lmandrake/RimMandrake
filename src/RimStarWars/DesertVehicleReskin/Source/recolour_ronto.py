#!/usr/bin/env python3
"""Shift the RONTO hide from olive to warm dun, so it is not the same animal as a dewback.

WHY A RECOLOUR AND NOT A REGENERATION
  Both species came back olive: measured over opaque non-keyline pixels, the south pairs
  sit at hue 51.1 (ronto) against 54.9 (dewback) -- 3.8 degrees apart, which at sprite
  size is no difference at all. DECIDE's ladder needs them distinct: CoveredCarriage is
  ronto x2, WarChariot is dewback x2, Chariot is dewback x1.
  A recolour cannot move a single pixel of silhouette, and silhouette is the only thing
  validate_sprite.py grades hard. A regeneration can, and costs a generation. So the
  dewback keeps the olive baseline and the RONTO moves.

WHAT IT DOES, and it is one HSV delta applied to every opaque pixel
  hue  -20 degrees      olive-yellow -> warm brown. A DELTA, not a remap: the harness
                        leather and the brass rings keep their relationship to the hide
                        instead of flattening to one colour.
  sat  x1.00            LEFT ALONE, and that is a measured choice. The hide is already
                        desaturated (S 0.33) and dun IS a desaturated brown; cutting it
                        further -- x0.78 and x0.70 were both rendered and looked at --
                        lands on a rosy grey, because a low-chroma warm hue over the
                        drawing's bright dorsal gradient reads pink, not dun.
  val  x1.10            dun is LIGHTER than olive at the same chroma, and the tonal gap
                        is what separates the two beasts at 128 px where hue alone is a
                        few pixels wide. Clips 2.2% of south and 0.01% of east, and those
                        pixels are the already near-white yoke bar and highlight rims.

  Near-black keyline pixels are untouched by construction -- a hue rotation on V<0.1 is a
  no-op -- so the drawing's line weight survives exactly.

Usage: recolour_ronto.py --input <keyed ronto png> --out <new png>
       Writes a NEW file. It never overwrites its input; the olive originals stay as the
       provenance of what the model actually returned.
"""
import argparse

import numpy as np
from PIL import Image

HUE_DEG = -20.0
SAT_GAIN = 1.00
VAL_GAIN = 1.10


def recolour(a):
    """a: HxWx4 uint8 RGBA. Returns a new array with the hide shifted."""
    out = a.copy()
    m = a[..., 3] > 0
    rgb = a[m][:, :3].astype(np.float32) / 255.0
    r, g, b = rgb[:, 0], rgb[:, 1], rgb[:, 2]
    mx, mn = rgb.max(1), rgb.min(1)
    d = mx - mn
    v = mx
    s = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0.0)
    h = np.zeros_like(v)
    nz = d > 1e-6
    ir, ig, ib = (mx == r) & nz, (mx == g) & nz, (mx == b) & nz
    h[ir] = ((g - b)[ir] / d[ir]) % 6.0
    h[ig] = ((b - r)[ig] / d[ig]) + 2.0
    h[ib] = ((r - g)[ib] / d[ib]) + 4.0
    h = (h * 60.0 + HUE_DEG) % 360.0
    s = np.clip(s * SAT_GAIN, 0.0, 1.0)
    v = np.clip(v * VAL_GAIN, 0.0, 1.0)

    c = v * s
    x = c * (1 - np.abs((h / 60.0) % 2 - 1))
    mm = v - c
    z = np.zeros_like(c)
    seg = (h / 60.0).astype(np.int32) % 6
    rr = np.select([seg == 0, seg == 1, seg == 2, seg == 3, seg == 4, seg == 5], [c, x, z, z, x, c])
    gg = np.select([seg == 0, seg == 1, seg == 2, seg == 3, seg == 4, seg == 5], [x, c, c, x, z, z])
    bb = np.select([seg == 0, seg == 1, seg == 2, seg == 3, seg == 4, seg == 5], [z, z, x, c, c, x])
    new = np.stack([rr + mm, gg + mm, bb + mm], 1)
    out[m, :3] = np.clip(new * 255.0 + 0.5, 0, 255).astype(np.uint8)
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    if a.input == a.out:
        raise SystemExit("refusing to overwrite the olive original: give a NEW --out")
    src = np.array(Image.open(a.input).convert("RGBA"))
    dst = recolour(src)
    Image.fromarray(dst).save(a.out)

    def stat(arr):
        m = arr[..., 3] > 200
        px = arr[m][:, :3].astype(np.float32)
        body = px[px.mean(1) > 60]
        import colorsys
        hsv = np.array([colorsys.rgb_to_hsv(*(q / 255)) for q in body[::401]])
        return body.mean(0), hsv[:, 0].mean() * 360, hsv[:, 1].mean(), hsv[:, 2].mean()

    b0, h0, s0, v0 = stat(src)
    b1, h1, s1, v1 = stat(dst)
    print("  %s -> %s" % (a.input.rsplit("/", 1)[-1], a.out.rsplit("/", 1)[-1]))
    print("    delta      hue %+.0f deg   sat x%.2f   val x%.2f" % (HUE_DEG, SAT_GAIN, VAL_GAIN))
    print("    body HSV   H %.1f -> %.1f   S %.3f -> %.3f   V %.3f -> %.3f" % (h0, h1, s0, s1, v0, v1))
    print("    body RGB   (%.0f,%.0f,%.0f) -> (%.0f,%.0f,%.0f)   per-channel gain %.3f/%.3f/%.3f"
          % (*b0, *b1, b1[0] / b0[0], b1[1] / b0[1], b1[2] / b0[2]))


if __name__ == "__main__":
    main()
