#!/usr/bin/env python3
"""fit_head_canvas.py — fit a full-canvas head render onto the engine's humanlike-head canvas.

Artpipe head renders fill 51-96% of their 512 canvas; vanilla and our borrowed heads fill
about 36% (bbox ~186x205 px, chin near y=362). Wired as-is a new head draws 1.5-2.7x too big.
This scales ONE species' facings by ONE factor (from the south facing's bbox height, so the
species keeps its relative size across facings) and re-places each facing on a 512 canvas with
the chin at the vanilla chin line. No repainting: a uniform LANCZOS resize and a translate.

usage: fit_head_canvas.py --target-h 240 --out DIR south.png east.png north.png
writes DIR/<stem>_south.png etc. (stem = --stem)
"""
import argparse
import os

from PIL import Image

CANVAS = 512
CHIN_Y = 365          # bottom of the borrowed heads' bbox (measured: 357-417, Cathar 362)
CENTER_X = {"south": 256, "north": 256, "east": 270}   # east heads sit slightly forward


def bbox(im):
    return im.getchannel("A").point(lambda a: 255 if a > 16 else 0).getbbox()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-h", type=int, default=240, help="south bbox height after fit, px of 512")
    ap.add_argument("--stem", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("south")
    ap.add_argument("east")
    ap.add_argument("north")
    a = ap.parse_args()
    ims = {f: Image.open(p).convert("RGBA") for f, p in (("south", a.south), ("east", a.east), ("north", a.north))}
    sb = bbox(ims["south"])
    s = a.target_h / (sb[3] - sb[1])
    os.makedirs(a.out, exist_ok=True)
    for f, im in ims.items():
        b = bbox(im)
        crop = im.crop(b)
        w, h = max(1, round(crop.width * s)), max(1, round(crop.height * s))
        crop = crop.resize((w, h), Image.LANCZOS)
        out = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
        x = CENTER_X[f] - w // 2
        y = min(CHIN_Y - h, CANVAS - h)
        out.paste(crop, (max(0, x), max(0, y)), crop)
        p = os.path.join(a.out, f"{a.stem}_{f}.png")
        out.save(p)
        print(f"{p}  scale {s:.3f}  bbox {bbox(out)}")


if __name__ == "__main__":
    main()
