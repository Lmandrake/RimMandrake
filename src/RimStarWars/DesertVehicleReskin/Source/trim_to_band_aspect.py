#!/usr/bin/env python3
"""Crop a keyed beast PNG so its SUBJECT BBOX matches its band's aspect exactly.

WHY THIS EXISTS, and it is not optional. build_beast_vehicle.py trims the pair to
its bbox before fitting, so the BBOX's aspect -- not the canvas's -- decides the
contain fit. A bbox whose aspect differs from the band's makes the fit spend its
bounded 12% stretch on one axis only, and the result is a stretched animal that
validate_sprite.py PASSES (it grades the whole sprite, and the band is a fraction
of it) while reading plainly wrong at sprite size. Cost two rebuilds on 2026-08-21.

Padding cannot fix it: the builder trims first, so any transparent pad is removed
before the fit ever sees it. The only lever is cropping subject pixels.

WHERE THE CUT COMES FROM, and east takes it off the LEFT
  The obvious rule -- cut at the end AWAY from the hitch -- is WRONG for east, and
  the donor crop is what says so. `donor_OxCart_east_6x.png` shows the band holding
  torsos and heads with the muzzles ON its right edge; the traces cross the band and
  run out of it to the LEFT, toward the cart. Our generations copy that: the right
  end of the bbox is the muzzle tip and the left ~300 px is trace and nothing else.
  Taking surplus width off the right therefore removes the snout, while taking it off
  the left removes trace-only columns the donor's band does not contain either -- so
  the left cut both preserves the drawing and moves our bbox CLOSER to the donor's
  framing. Nothing unwelds: the fit anchors at the hitch and spans the full band, so
  the shortened trace still reaches the band's left edge and meets the cart.
  Surplus HEIGHT has no free end -- both edges are drawing -- so it is split evenly
  top and bottom, keeping the beast centred on its own ground line.

THE CAP, and why the dewbacks need one
  A dewback is a long low lizard with a tail half its own length, so its bbox comes
  out 1.90 (pair) to 2.56 (single) against bands of 1.50 and 1.53. Cutting all of
  that off the left would reach the hind leg. --max-cut bounds the crop as a fraction
  of bbox width; whatever aspect error survives it is handed to the builder's contain
  fit, which is bounded at 12% and prints what it actually spent. Cutting UP TO the
  cap is still worth doing even when it cannot close the gap: every column removed
  makes the beast bigger inside the band. On the single it takes the fitted height
  from 102 rows to 146 of a 152-row band.

Usage:  trim_to_band_aspect.py <Vehicle> <facing> --input keyed.png --out trimmed.png
"""
import argparse
import sys

from PIL import Image

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from build_beast_vehicle import BANDS  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("vehicle")
    p.add_argument("facing")
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--max-cut", type=float, default=1.0,
                   help="most of the bbox WIDTH the aspect crop may take, as a fraction")
    p.add_argument("--cut", choices=("left", "right"), default="left",
                   help="which end surplus WIDTH comes off; see the docstring")
    a = p.parse_args()

    x0, x1, y0, y1 = BANDS[(a.vehicle, a.facing)]
    bw, bh = x1 - x0 + 1, y1 - y0 + 1
    target = bw / bh

    im = Image.open(a.input).convert("RGBA")
    im = im.crop(im.getbbox())
    w0, h0 = im.size
    have0 = w0 / h0

    # ⚠️ RE-BBOX AFTER EVERY CUT AND ITERATE. Cutting the trace end also removes the only
    # rows a trace occupied, so the bbox gets SHORTER as well as narrower and the aspect
    # moves again -- on the single dewback one pass reported 1.788 and the builder then
    # measured 1.949 off the same file. Loop until the crop is a no-op.
    cut = "nothing"
    for _ in range(8):
        im = im.crop(im.getbbox())
        w, h = im.size
        have = w / h
        if have > target:                  # too wide -> take it off the trace end
            nw = max(int(round(h * target)), int(round(w0 * (1 - a.max_cut))))
            if nw >= w:
                break
            im = im.crop((w - nw, 0, w, h)) if a.cut == "left" else im.crop((0, 0, nw, h))
            cut = "width -%d px off the %s" % (w0 - nw, a.cut)
        elif have < target:                # too tall -> split evenly, no free end exists
            nh = int(round(w / target))
            if nh >= h:
                break
            top = (h - nh) // 2
            im = im.crop((0, top, w, top + nh))
            cut = "height -%d px, %d top / %d bottom" % (h - nh, top, h - nh - top)
        else:
            break

    im = im.crop(im.getbbox())
    im.save(a.out)
    print("  %s %s  band %dx%d aspect %.4f" % (a.vehicle, a.facing, bw, bh, target))
    print("    bbox   %dx%d aspect %.4f  (%+.1f%% off band)"
          % (w0, h0, have0, (have0 / target - 1) * 100))
    print("    cut    %s" % cut)
    print("    wrote  %s  %dx%d aspect %.4f  (%+.1f%% off band)"
          % (a.out, im.size[0], im.size[1], im.size[0] / im.size[1],
             (im.size[0] / im.size[1]) / target * 100 - 100))


if __name__ == "__main__":
    main()
