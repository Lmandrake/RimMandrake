#!/usr/bin/env python3
"""Hose UNDER-COUPLER sprites, one pair per look (owner ruling 2026-10-23, by card: couplers' art goes UNDER the fixture).

Writes <outdir>/<Look>/UnderCollar.png and UnderPipe.png -- the art Machinery/UnderCouplerGeometry.cs draws beneath a tank or
machine where a hose is coupled. Each canvas is exactly its quad at 256 px/cell, +u (left -> right) pointing INTO the
fixture: the collar's left edge is the port point, where the hose's brass coupling face meets it.

  UnderCollar  36 x 80 px (0.140625 x 0.3125 cell): face ring, a groove (the look's accent), the collar body
  UnderPipe    32 x 56 px (stretched along, 0.21875 cell wide): a plain cylinder of the look's pipe material

Materials are port_fittings.MATERIALS (coupler colour for the collar, nipple colour for the pipe), so the under-couplers
match the fittings the looks already use. Deterministic (fixed grain seeds).

  python3 under_couplers.py <outdir>
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "TankPorts"))
import modern_port_fittings as mpf  # noqa: E402
import port_fittings as pf  # noqa: E402

LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")
COLLAR = (36, 80)   # along, cross (px) -- UnderCouplerGeometry.CollarLength / CollarWidth x 256
PIPE = (32, 56)     # along (stretched), cross -- PipeWidth x 256


def _grain(img, seed, amp):
    img[..., :3] = np.clip(img[..., :3] * pf._grain(img.shape[:2], seed, amp)[..., None], 0, 255)


def collar(look):
    along, cross = COLLAR
    _, _, cpl, accent = pf.MATERIALS[look]
    cpl = np.array(cpl, float)
    c = np.zeros((cross, along, 4), float)
    cy = cross / 2.0
    mpf.part(c, 6.0, along, cy, 36.0, cpl * 0.9, True)                                   # collar body
    mpf.part(c, 0.0, 7.0, cy, 39.5, cpl, True)                                           # face ring (the port face)
    mpf.part(c, 7.0, 9.5, cy, 34.0, np.array(accent, float) if accent else cpl * 0.7, False)   # groove
    mpf.part(c, 20.0, 24.0, cy, 37.5, cpl * 0.8, True)                                   # second bead
    _grain(c, 11 + LOOKS.index(look), 0.08)
    return Image.fromarray(np.clip(c, 0, 255).astype(np.uint8), "RGBA")


def pipe(look):
    along, cross = PIPE
    nip = np.array(pf.MATERIALS[look][1], float)
    c = np.zeros((cross, along, 4), float)
    mpf.part(c, 0.0, along, cross / 2.0, cross / 2.0 - 0.5, nip, False)
    return Image.fromarray(np.clip(c, 0, 255).astype(np.uint8), "RGBA")


def build():
    """{(look, piece): PIL RGBA image}."""
    out = {}
    for look in LOOKS:
        out[(look, "UnderCollar")] = collar(look)
        out[(look, "UnderPipe")] = pipe(look)
    return out


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    for (look, piece), im in build().items():
        d = os.path.join(argv[1], look)
        os.makedirs(d, exist_ok=True)
        im.save(os.path.join(d, piece + ".png"))
        print("wrote", os.path.join(d, piece + ".png"), im.size)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
