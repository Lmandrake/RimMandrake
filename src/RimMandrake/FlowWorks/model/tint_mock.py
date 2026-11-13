#!/usr/bin/env python3
"""Mock the pit-water tint (model/underliquid.py) over REAL captures, today's draw against the new law.

    python3 src/RimMandrake/FlowWorks/model/tint_mock.py <captures_dir> <out_dir>

<captures_dir> holds the 2026-11-12 evening live captures (BP0_dry_close.png, BP3_close_corpses.png, BP5_deepest_close.png,
D8_F0_F4.png, D8_F4_F8.png). Writes:
  mock_d8_row_old_vs_new.png     top: today's D8 F1..F8 (0.5..4 m of water in a 4 m pit) as captured; bottom: the dry big
                                 pit (BP0) under the new sheet at the same depths
  mock_bigpit_old_vs_new.png     top: today's BP0 dry, BP3 2 m, BP5 4 m as captured; bottom: BP0 under the new sheet at
                                 0, 0.5, 1, 2, 3, 4 m
  mock_liquids.png               the same crop under 2 m of each clear liquid (each keeps its own colour) and tar
A mock is a model picture, not the game: every pixel of the pit is treated as lying on the floor (a standing thing's top
is a little less tinted in game), and labels are tinted here where the game fades them. The live look decides.
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import underliquid as U  # noqa: E402

SCALE = 2566 / 2419  # the captures were read at 2419 wide; boxes below are in those display pixels
BP_PIT = (435, 0, 1890, 1340)           # the big pit's inside (floor and drowned west wall) in BP0/BP3/BP5
BP_CROP = (430, 360, 1900, 1345)        # the part with things in it
D8_CELLS = [(420, 585, 762, 927), (970, 585, 1312, 927), (1520, 585, 1862, 927), (2070, 585, 2412, 927)]
TILE_W = 400
WATER = 0.45
LIQUIDS = [("fresh water", 0.45, (0.62, 0.80, 0.98)), ("salt water", 0.35, (0.42, 0.62, 0.82)),
           ("acid water", 0.25, (0.78, 0.96, 0.22)), ("toxic water", 0.35, (0.58, 0.72, 0.28)),
           ("rust water", 0.35, (0.66, 0.36, 0.23)), ("violet water", 0.35, (0.47, 0.31, 0.66)),
           ("tar", 0.0, (0.16, 0.15, 0.14))]


def box(b):
    return tuple(int(round(v * SCALE)) for v in b)


def tint(img, pit_box, level, clarity, colour):
    """The new draw: the floor and everything on it as dry, one even sheet of the body colour at 1 - seen(level)."""
    out = img.copy()
    if level <= 0:
        return out
    if clarity <= 0:
        cover = Image.new("RGB", (pit_box[2] - pit_box[0], pit_box[3] - pit_box[1]), tuple(int(v * 255) for v in colour))
        out.paste(cover, pit_box[:2])
        return out
    s = U.seen(clarity, level)
    b = tuple(int(255 * v) for v in U.body(colour))
    region = out.crop(pit_box)
    sheet = Image.new("RGB", region.size, b)
    out.paste(Image.blend(region, sheet, 1 - s), pit_box[:2])
    return out


def label(img, text):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, img.width, 22], fill=(0, 0, 0))
    d.text((6, 5), text, fill=(255, 255, 255))
    return img


def tile(img, crop, text):
    t = img.crop(crop)
    t = t.resize((TILE_W, int(t.height * TILE_W / t.width)))
    return label(t, text)


def sheet_of(rows, path):
    w = max(sum(t.width for t in r) for r in rows)
    h = sum(max(t.height for t in r) for r in rows)
    out = Image.new("RGB", (w + 4 * max(len(r) for r in rows), h + 4 * len(rows)), (255, 255, 255))
    y = 0
    for r in rows:
        x = 0
        for t in r:
            out.paste(t, (x, y))
            x += t.width + 4
        y += max(t.height for t in r) + 4
    out.save(path)
    return path


def op(m):
    return 1 - U.seen(WATER, m)


def main():
    cap, out = sys.argv[1], sys.argv[2]
    bp0 = Image.open(os.path.join(cap, "BP0_dry_close.png")).convert("RGB")
    pit, crop = box(BP_PIT), box(BP_CROP)
    d8a = Image.open(os.path.join(cap, "D8_F0_F4.png")).convert("RGB")
    d8b = Image.open(os.path.join(cap, "D8_F4_F8.png")).convert("RGB")
    depths = [0.5 * n for n in range(1, 9)]
    today = [tile(d8a if i < 4 else d8b, box(D8_CELLS[i % 4]), "TODAY D8 F%d %.1f m" % (i + 1, m))
             for i, m in enumerate(depths)]
    new = [tile(tint(bp0, pit, m, WATER, LIQUIDS[0][2]), crop, "NEW %.1f m  hides %.0f%%" % (m, 100 * op(m)))
           for m in depths]
    for t in today + new:
        t.thumbnail((300, 1000))
    p1 = sheet_of([today[:4], today[4:], new[:4], new[4:]], os.path.join(out, "mock_d8_row_old_vs_new.png"))
    old_row = [tile(Image.open(os.path.join(cap, f)).convert("RGB"), crop, "TODAY " + t) for f, t in
               [("BP0_dry_close.png", "BP0 dry"), ("BP3_close_corpses.png", "BP3 2 m"), ("BP5_deepest_close.png", "BP5 4 m")]]
    new_row = [tile(tint(bp0, pit, m, WATER, LIQUIDS[0][2]), crop, "NEW %.1f m  hides %.0f%%" % (m, 100 * op(m)))
               for m in (0.0, 0.5, 1.0, 2.0, 3.0, 4.0)]
    p2 = sheet_of([old_row, new_row[:3], new_row[3:]], os.path.join(out, "mock_bigpit_old_vs_new.png"))
    liq = [tile(tint(bp0, pit, 2.0, c, col), crop, "NEW 2 m %s" % n) for n, c, col in LIQUIDS]
    p3 = sheet_of([liq[:4], liq[4:]], os.path.join(out, "mock_liquids.png"))
    print("\n".join((p1, p2, p3)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
