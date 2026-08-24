#!/usr/bin/env python3
"""Carve a dark face cavity into the hooded-Jawa faction icon.

The icon shipped as a flat grey sack with two white eyes sitting on the SAME grey as the hood
exterior, so it read as a sack with eye holes rather than a face in shadow. Owner, 2026-08-24:
*"they have dark faces beneath their hood. Right now it looks like they're wearing a sack over
their head with eye holes."*

🔑 **Deterministic edit, not a regeneration.** The silhouette and the black outline are the part
that already works; a generator would move them. This only repaints interior luminance.
"""
import argparse, os
import numpy as np
from PIL import Image

# Measured off the shipped icon, 128x128: eyes span x 47-83, y 77-90; hood grey x 26-101, y 15-112.
CAVITY_CX, CAVITY_CY = 64.5, 86.0
CAVITY_RX, CAVITY_RY = 30.0, 30.0
FEATHER = 0.42          # fraction of the radius over which the shadow fades back to hood grey
CAVITY_LUMA = 14        # near-black, but not the outline's 0 -- the outline must stay readable
GLOW_RADIUS = 9.0       # soft light around each eye, inside the cavity


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("icon")
    ap.add_argument("--out")
    ap.add_argument("--cx", type=float, default=CAVITY_CX)
    ap.add_argument("--cy", type=float, default=CAVITY_CY)
    ap.add_argument("--rx", type=float, default=CAVITY_RX)
    ap.add_argument("--ry", type=float, default=CAVITY_RY)
    ap.add_argument("--feather", type=float, default=FEATHER)
    ap.add_argument("--luma", type=int, default=CAVITY_LUMA)
    ap.add_argument("--glow", type=float, default=GLOW_RADIUS)
    a = ap.parse_args()

    im = np.array(Image.open(a.icon).convert("RGBA")).astype(float)
    alpha, L = im[..., 3], im[..., 0]
    opaque = alpha > 128

    # Three regions, separated by luminance. The outline is structural and is never touched.
    outline = opaque & (L < 40)
    eyes    = opaque & (L > 200)
    hood    = opaque & ~outline & ~eyes
    base    = float(np.median(L[hood])) if hood.any() else 108.0

    h, w = L.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    d = np.sqrt(((xx - a.cx) / a.rx) ** 2 + ((yy - a.cy) / a.ry) ** 2)

    # 1 inside the cavity core, ramping to 0 across the feather band.
    shade = np.clip((1.0 - d) / max(a.feather, 1e-6), 0.0, 1.0)
    shade = shade * shade * (3 - 2 * shade)                      # smoothstep: no visible seam

    # Wipe the original bloom back to flat hood grey, then lay the cavity in.
    out_L = np.where(hood | eyes, base, L)
    paint = hood | eyes
    out_L = np.where(paint, out_L * (1 - shade) + a.luma * shade, out_L)

    # The eyes go back on top, bright, plus a tight glow that only lifts the cavity around them.
    if a.glow > 0 and eyes.any():
        ey, ex = np.nonzero(eyes)
        glow = np.zeros_like(out_L)
        for cx, cy in ((ex[ex < ex.mean()].mean(), ey[ex < ex.mean()].mean()),
                       (ex[ex >= ex.mean()].mean(), ey[ex >= ex.mean()].mean())):
            g = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * a.glow ** 2)))
            glow = np.maximum(glow, g)
        lift = np.clip(glow, 0, 1) * 150.0 * shade
        out_L = np.where(paint, np.minimum(out_L + lift, 255), out_L)
    out_L = np.where(eyes, 255.0, out_L)

    im[..., 0] = im[..., 1] = im[..., 2] = np.clip(out_L, 0, 255)
    dst = a.out or a.icon
    Image.fromarray(im.astype(np.uint8), "RGBA").save(dst)
    print("wrote %s  (hood grey %.0f, cavity %.0f)" % (dst, base, a.luma))


if __name__ == "__main__":
    main()
