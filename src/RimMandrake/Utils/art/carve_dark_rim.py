#!/usr/bin/env python3
"""carve_dark_rim.py — give an edited creature sprite back the dark outline its source had.

    python3 src/RimMandrake/Utils/art/carve_dark_rim.py <in.png> <out.png> [--width 3]

WHY: an image edit (codex $imagegen) of an outlined RimWorld sprite tends to return the subject with its black rim
faded to a 1-2 px brown line, so the edited variant reads softer than the facings beside it. This paints the outer
`width` px band of the opaque silhouette (alpha > 128) and the partially transparent fringe black, INWARD, so the
footprint does not grow (a sprite whose bbox already sits 3 px from the canvas edge stays inside it). Alpha 1..8 is
zeroed: an invisible fringe poisons later bbox measurements. First used for MIASMA_WARDEN_MOTHER_ART_1 (aged set).

Install the result through the art ledger with --reason script:src/RimMandrake/Utils/art/carve_dark_rim.py.
"""
import argparse

from PIL import Image, ImageChops, ImageFilter


def carve(im: Image.Image, width: int = 3) -> Image.Image:
    im = im.convert("RGBA")
    a = im.getchannel("A").point(lambda v: 0 if v <= 8 else v)
    solid = a.point(lambda v: 255 if v > 128 else 0)
    band = ImageChops.subtract(solid, solid.filter(ImageFilter.MinFilter(2 * width + 1)))
    black = Image.new("RGBA", im.size, (0, 0, 0, 255))
    im.putalpha(a)
    out = Image.composite(black, im, band)
    out = Image.composite(black, out, a.point(lambda v: 255 if 0 < v <= 128 else 0))
    out.putalpha(a)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--width", type=int, default=3)
    ns = ap.parse_args()
    carve(Image.open(ns.src), ns.width).save(ns.dst)


if __name__ == "__main__":
    main()
