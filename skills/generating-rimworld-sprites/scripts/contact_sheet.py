#!/usr/bin/env python3
"""contact_sheet.py — lay candidates beside the reference for a human verdict.

The validator decides whether a sprite is *shippable*. It cannot decide whether
it is *good* - style match, readability and art direction need eyes. This makes
that judgement cheap by putting everything on one image.

Two rows, because sprites fail differently at the two sizes:
  top     large, for judging craft and damage shape
  bottom  true in-game size, for judging whether it reads at all

Everything is composited over a checkerboard, so transparency is visible rather
than being mistaken for black.

    python contact_sheet.py --reference ref.png --out sheet.png a.png b.png c.png

Exit codes: 0 ok, 2 unusable input.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]
                       / "generating-images" / "scripts"))
import pnglib  # noqa: E402

# Sprites are judged at two scales. 420px shows craft; 96px is close to what a
# 3x4-tile building actually occupies on screen at default zoom, which is where
# "reads as brown mud" becomes obvious.
LARGE_H = 420
SMALL_H = 96
PAD = 16
GAP = 14


def composite(dst: bytearray, dw: int, sprite, ox: int, oy: int) -> None:
    sw, sh, spx = sprite
    for y in range(sh):
        for x in range(sw):
            a = spx[(y * sw + x) * 4 + 3] / 255.0
            if a <= 0:
                continue
            d = ((y + oy) * dw + (x + ox)) * 3
            for c in range(3):
                dst[d + c] = int(spx[(y * sw + x) * 4 + c] * a + dst[d + c] * (1 - a))


def scaled(path: Path, height: int):
    w, h, px = pnglib.read_png(str(path))
    nw = max(1, round(w * height / h))
    return nw, height, pnglib.resize_rgba(w, h, px, nw, height)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--reference", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("candidates", nargs="+")
    ap.add_argument("--large", type=int, default=LARGE_H)
    ap.add_argument("--small", type=int, default=SMALL_H)
    args = ap.parse_args()

    paths = [Path(args.reference)] + [Path(c) for c in args.candidates]
    for p in paths:
        if not p.is_file():
            print(f"ERROR no such file: {p}", file=sys.stderr)
            return 2

    big = [scaled(p, args.large) for p in paths]
    small = [scaled(p, args.small) for p in paths]

    row_w = sum(s[0] for s in big) + GAP * (len(big) - 1)
    width = row_w + PAD * 2
    height = PAD * 3 + args.large + args.small

    sheet = bytearray(pnglib.checkerboard(width, height))

    x = PAD
    for s in big:
        composite(sheet, width, s, x, PAD)
        x += s[0] + GAP

    # Bottom row is left-aligned under its own column so the eye can pair them.
    x = PAD
    y = PAD * 2 + args.large
    for i, s in enumerate(small):
        composite(sheet, width, s, x + (big[i][0] - s[0]) // 2, y)
        x += big[i][0] + GAP

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    pnglib.write_png(args.out, width, height, sheet)

    print(f"wrote {args.out}  ({width}x{height})")
    print("left to right:")
    for i, p in enumerate(paths):
        print(f"  {i}. {'REFERENCE  ' if i == 0 else '           '}{p.name}")
    print(f"\ntop row {args.large}px for craft, bottom row {args.small}px for "
          f"whether it reads in game")
    return 0


if __name__ == "__main__":
    sys.exit(main())
