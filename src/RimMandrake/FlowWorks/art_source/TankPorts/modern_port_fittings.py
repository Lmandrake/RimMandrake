#!/usr/bin/env python3
"""MODERN_TANK_PORT_REDRAW_COUPLER_FLOATS -- draw hose-port fittings on the west and east sides of the Modern tall / IBC /
extra-tall tank art, where the hose couples to these tanks: TankPortGeometry.PortPoint is measured for RM_LiquidTank only
(RM_MapComponent_Hoses.PortEnd), so on these three the hose end couples at the shared edge's MIDPOINT -- the footprint
edge, at the end cell's centre: dz = -0.5 (south lane) or +0.5 (north lane) from the footprint centre. One fitting per
lane per side, four per tank.

Those three pictures are narrower than the 2x2 footprint and drew nothing at the port, so the hose coupler stopped at
the footprint edge ~0.3 cell off the wall and a bare hose stub ran on into a plain wall (live look 2026-10-22). Each
side gets, from the wall outward: a black PP bulkhead nut on the wall, a grey PVC nipple, and an aluminium camlock
male adapter whose face is the canvas edge (= the footprint edge at drawSize width 2). Everything else is unchanged.

Base = the owner's card picks as installed in fb34c9bc2d (read from git), so re-running is reproducible.
  python3 modern_port_fittings.py <outdir>     writes the three PNGs into <outdir>
"""
import io
import os
import subprocess
import sys

import numpy as np
from PIL import Image

BASE_COMMIT = "fb34c9bc2d"
REL = "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Tank/Modern/%s.png"
LANE_DZ = (-0.5, 0.5)
# def -> (drawSize z, drawOffset z); the footprint is 2x2 and drawSize x is 2 for all three
TANKS = {
    "RM_LiquidTankTall": (3.0, 0.5),
    "RM_UniversalCargoTank": (2.0, 0.0),
    "RM_UniversalCargoTankXTall": (4.0, 1.0),
}
PX_PER_CELL = 256.0

PP_BLACK = np.array([46, 48, 52], float)
PVC_GREY = np.array([96, 101, 108], float)
ALU = np.array([186, 190, 196], float)


def shade(t):
    """Cylinder lighting across the section, t in [-1, 1] top->bottom; light from the upper left like the art."""
    n = np.sqrt(np.clip(1 - t * t, 0, 1))
    lam = 0.35 + 0.65 * np.clip(0.45 * -t + 0.89 * n, 0, 1)
    spec = np.exp(-((t + 0.42) / 0.16) ** 2) * 0.35
    return lam, spec


def part(canvas, x0, x1, cy, hh, colour, rim=False):
    """A horizontal cylinder segment x0..x1 (canvas px), centre row cy (float), half-height hh, anti-aliased top/bottom."""
    h = canvas.shape[0]
    rows = np.arange(h, dtype=float)
    t = (rows + 0.5 - cy) / hh
    cover = np.clip(hh - np.abs(rows + 0.5 - cy) + 0.5, 0, 1)
    lam, spec = shade(np.clip(t, -1, 1))
    edge = np.clip((np.abs(t) - 0.86) / 0.14, 0, 1) * 0.45          # darker silhouette line
    for x in range(int(np.floor(x0)), int(np.ceil(x1))):
        cx = np.clip(min(x + 1 - x0, x1 - x), 0, 1)
        a = cover * cx
        col = colour[None, :] * (lam * (1 - edge))[:, None] + 255 * spec[:, None]
        if rim and (x - x0 < 1.5 or x1 - x < 1.5):
            col = col * 0.7
        col = np.clip(col, 0, 255)
        sel = a > 0
        src_a = a[sel]
        dst = canvas[sel, x]
        out_a = src_a + dst[:, 3] / 255.0 * (1 - src_a)
        rgb = (col[sel] * src_a[:, None] + dst[:, :3] * (dst[:, 3:4] / 255.0) * (1 - src_a[:, None])) / np.maximum(out_a[:, None], 1e-6)
        canvas[sel, x, :3] = rgb
        canvas[sel, x, 3] = out_a * 255


def fitting(canvas, cy, wall, west):
    """Draw one side's fitting. wall = first opaque column of the tank on that side at row cy (distance from the edge)."""
    w = canvas.shape[1]
    sub = np.zeros_like(canvas)
    # distances from the canvas edge
    pieces = [   # half-heights cover the hose's centre stub (~0.2 cell) that runs on under the building
        (0.0, 7.0, 35.0, ALU, True),                 # camlock adapter face ring
        (7.0, 9.0, 31.0, ALU * 0.75, False),         # groove for the cam arms
        (9.0, 20.0, 33.0, ALU, True),                # adapter body
        (20.0, 26.0, 31.0, ALU * 0.9, True),         # hex/thread shoulder
        (26.0, wall - 9.0, 30.0, PVC_GREY, False),   # PVC nipple
        (wall - 13.0, wall + 3.0, 41.0, PP_BLACK, True),   # bulkhead nut on the wall
    ]
    for a, b, hh, col, rim in pieces:
        part(sub, a, b, cy, hh, col, rim)
    if not west:
        sub = sub[:, ::-1]
    m = sub[..., 3:4] / 255.0
    base_a = canvas[..., 3:4] / 255.0
    out_a = m + base_a * (1 - m)
    canvas[..., :3] = (sub[..., :3] * m + canvas[..., :3] * base_a * (1 - m)) / np.maximum(out_a, 1e-6)
    canvas[..., 3:4] = out_a * 255


def build(name):
    blob = subprocess.run(["git", "show", "%s:%s" % (BASE_COMMIT, REL % name)], capture_output=True, check=True,
                          cwd=os.path.dirname(os.path.abspath(__file__)), timeout=60).stdout
    im = Image.open(io.BytesIO(blob)).convert("RGBA")
    a = np.array(im).astype(float)
    h, w = a.shape[:2]
    dsz, off = TANKS[name]
    top = dsz / 2.0 + off                                  # cells from the footprint centre up to the canvas top
    cys = []
    for dz in LANE_DZ:
        cy = (top - dz) / dsz * h                           # port row (float, canvas px)
        band = a[int(cy) - 8:int(cy) + 9, :, 3] > 128       # the wall under the whole nut, not one row
        cols = np.nonzero(band.any(axis=0))[0]
        fitting(a, cy, float(cols[0]), True)
        fitting(a, cy, float(w - 1 - cols[-1]), False)
        cys.append(round(cy, 1))
    return Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8), "RGBA"), cys


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for name in TANKS:
        im, cy = build(name)
        im.save(os.path.join(out, name + ".png"), optimize=True)
        print("%s: port rows %s -> %s" % (name, cy, os.path.join(out, name + ".png")))


if __name__ == "__main__":
    main()
