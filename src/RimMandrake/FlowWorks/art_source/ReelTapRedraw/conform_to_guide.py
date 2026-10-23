#!/usr/bin/env python3
"""REEL_TAP_CAMERA_REDRAW_STILL_SIDE_ON: put a generated candidate onto the game canvas where its camera guide put the
drawing (NOT onto the old side-on art's box: the redraw changes the silhouette on purpose). The raw's alpha bbox
(alpha > 128) is scaled uniformly (mean of the width/height ratios) onto the guide's subject bbox, premultiplied BOX
downscale, faint alpha (< 8) cleared.
usage: conform_to_guide.py <raw.png> <guide.png (1024, white ground)> <out.png> [--canvas 256]"""
import sys
import numpy as np
from PIL import Image


def premul_resize(im, size):
    a = np.asarray(im.convert("RGBA")).astype(np.float64) / 255.0
    pm = np.dstack([a[..., :3] * a[..., 3:4], a[..., 3:4]])
    ch = [Image.fromarray(pm[..., i].astype(np.float32), "F").resize(size, Image.BOX) for i in range(4)]
    r = np.dstack([np.asarray(c) for c in ch])
    al = r[..., 3:4]
    rgb = np.where(al > 1e-6, r[..., :3] / np.maximum(al, 1e-6), 0)
    out = np.dstack([np.clip(rgb, 0, 1), al])
    out = (out * 255 + 0.5).astype(np.uint8)
    out[out[..., 3] < 8] = 0
    return Image.fromarray(out, "RGBA")


def main(raw, guide, out, canvas=256):
    g = np.asarray(Image.open(guide).convert("L")) < 250
    ys, xs = np.nonzero(g)
    k = canvas / g.shape[0]
    gx0, gx1, gy0, gy1 = xs.min() * k, (xs.max() + 1) * k, ys.min() * k, (ys.max() + 1) * k
    im = Image.open(raw).convert("RGBA")
    a = np.asarray(im)[..., 3] > 128
    ry, rx = np.nonzero(a)
    crop = im.crop((rx.min(), ry.min(), rx.max() + 1, ry.max() + 1))
    sw, sh = (gx1 - gx0) / crop.width, (gy1 - gy0) / crop.height
    s = (sw + sh) / 2
    nw, nh = max(1, round(crop.width * s)), max(1, round(crop.height * s))
    small = premul_resize(crop, (nw, nh))
    cv = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    cx, cy = (gx0 + gx1) / 2, (gy0 + gy1) / 2
    cv.alpha_composite(small, (int(round(cx - nw / 2)), int(round(cy - nh / 2))))
    cv.save(out)
    print("%s scale_ratio w/h %.3f/%.3f (aspect drift %.1f%%) -> %dx%d at (%d,%d)" % (out, sw, sh, 100 * abs(sw / sh - 1), nw, nh, round(cx - nw / 2), round(cy - nh / 2)))


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1], a[2], int(a[a.index("--canvas") + 1]) if "--canvas" in a else 256)
