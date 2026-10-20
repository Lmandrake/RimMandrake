#!/usr/bin/env python3
"""head_facing_fix.py — two mechanical fixes for fitted painted heads (no repainting).

  shift <in.png> <out.png> --dy N     translate the picture N px down (negative = up) on its own canvas;
                                      refuses if any opaque pixel would leave the canvas.
                                      Use when one facing was painted higher/lower than the others
                                      (fit_head_canvas.py aligns each facing's bbox BOTTOM, so a facing whose
                                      lowest pixel is an ear tip, not the chin, rides high).
  mask  <ref.png> <out_m.png>         write a solid-black CutoutComplex mask the size of ref.png. Under
                                      CutoutComplex, mask red = tinted by colour one (skin), black = colorTwo
                                      (white for heads), so a black mask draws the painting exactly as painted.
"""
import argparse
import sys

from PIL import Image


def bbox(im):
    return im.getchannel("A").point(lambda a: 255 if a > 16 else 0).getbbox()


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("shift")
    s.add_argument("src")
    s.add_argument("out")
    s.add_argument("--dy", type=int, required=True)
    m = sub.add_parser("mask")
    m.add_argument("ref")
    m.add_argument("out")
    a = ap.parse_args()
    if a.cmd == "shift":
        im = Image.open(a.src).convert("RGBA")
        b = bbox(im)
        if b is None or b[1] + a.dy < 0 or b[3] + a.dy > im.height:
            sys.exit(f"REFUSED: bbox {b} shifted by {a.dy} leaves the {im.height}px canvas")
        out = Image.new("RGBA", im.size, (0, 0, 0, 0))
        out.paste(im, (0, a.dy))
        out.save(a.out)
        print(f"{a.out}  bbox {b} -> {bbox(out)}")
    else:
        ref = Image.open(a.ref)
        Image.new("RGB", ref.size, (0, 0, 0)).save(a.out)
        print(f"{a.out}  black mask {ref.size}")


if __name__ == "__main__":
    main()
