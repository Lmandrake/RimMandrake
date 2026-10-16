#!/usr/bin/env python3
"""conform.py -- raw codex renders -> candidate sprites at the proposed in-game geometry (premultiplied-alpha resize).

  pump   : canvas 512x512 = drawSize (2,2) at 256 px/cell, footprint 2x1 (drawOffset z +0.5, so the footprint is the
           canvas's lower half): the body spans 95% of the width, its base 12 px above the canvas bottom.
  flange : canvas 128x128 = drawSize (0.5,0.5); pipe enters from the left edge, flange at the right. Drawn at a pipe cell's
           edge facing a tank/pump (rotated per side by the draw hook).
  saddle : canvas 256x256 = drawSize (1,1); the pipe (0.227 cell, the rigid pipe's band) spans the full width, the spigot in the middle.
    python3 conform.py
"""
import os

from PIL import Image

H = os.path.dirname(os.path.abspath(__file__))
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]


def trim(im):
    a = im.split()[3].point(lambda v: 255 if v > 24 else 0)
    return im.crop(a.getbbox())


def fit(im, w, h):
    return im.convert("RGBa").resize((max(1, round(w)), max(1, round(h))), Image.LANCZOS).convert("RGBA")


def clean(im):
    """Zero the faint fringe (alpha < 8) the resize leaves."""
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y][3] < 8:
                px[x, y] = (0, 0, 0, 0)
    return im


def pump(src, out):
    t = trim(Image.open(src).convert("RGBA"))
    w = 0.95 * 512
    h = t.height * w / t.width
    c = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    c.alpha_composite(fit(t, w, h), (round((512 - w) / 2), round(512 - 12 - h)))
    clean(c).save(out)


def flange(src, out):
    t = trim(Image.open(src).convert("RGBA"))
    h = min(124, t.height * 128 / t.width)
    w = t.width * h / t.height
    c = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    c.alpha_composite(fit(t, w, h), (128 - round(w), round((128 - h) / 2)))
    clean(c).save(out)


def saddle(src, out):
    """Scaled so the pipe band (measured at the left edge) is the rigid pipe's own 0.227 cell = 58 px at 256 px/cell, then
    the middle cell cropped: canvas 256x256 = drawSize (1,1), the pipe across its middle."""
    t = trim(Image.open(src).convert("RGBA"))
    a = t.split()[3]
    rows = [y for y in range(t.height) if a.getpixel((3, y)) > 128]
    band, mid = rows[-1] - rows[0] + 1, (rows[0] + rows[-1]) / 2
    k = 58 / band
    big = fit(t, t.width * k, t.height * k)
    cx, cy = big.width / 2, mid * k
    c = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    c.alpha_composite(big.crop((round(cx - 128), round(cy - 128), round(cx + 128), round(cy + 128))))
    clean(c).save(out)


if __name__ == "__main__":
    for look in LOOKS:
        for piece, fn in (("pump", pump), ("flange", flange), ("saddle", saddle)):
            src = os.path.join(H, "raw", f"{look}_{piece}.png")
            if os.path.exists(src):
                fn(src, os.path.join(H, "cand", f"{look}_{piece}.png"))
                print("cand", look, piece)
