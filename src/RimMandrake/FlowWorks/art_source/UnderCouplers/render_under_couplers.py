#!/usr/bin/env python3
"""Offline composite of every hose-coupling fixture x look with a hose coupled on each port side, BEFORE (no under-coupler,
the hose's own stub ribbon to the centre as today) and AFTER (the under-coupler collar + pipe beneath the fixture,
its length from Source/Machinery/UnderCouplerReach.cs; a port listed -1 there keeps the BEFORE stub).

Draw order is the game's altitude order, bottom to top: ground, (after) under-coupler pipe then collar | (before) hose stub
to the footprint centre, hose strand, brass coupling, binding wrap, and the FIXTURE SPRITE on top (the hose band sits below
the building layer). Geometry: the constants in Source/Machinery/UnderCouplerGeometry.cs and the hose's (HoseMath flat
visible 0.18, coupling 1.5x at a tank/machine port, face on the port point); ports as selftest_hose_fittings.ports().
An approximation of the live draw (straight hose, flat pose, no shadows/tint), for a naive judge before the live look.

  python3 render_under_couplers.py <outdir>     one PNG per fixture x look: top = game scale (64 px/cell), bottom = 4x
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
FW = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, FW)
import selftest_hose_fittings as gate  # noqa: E402  (defs, ports, constants parsed from the C#)

TEX = os.path.join(FW, "Textures")
TABLE = gate.reach_table() or {}   # UnderCouplerReach.cs: the pipe ends beneath the first opaque body run (-1: none drawn)
HOSE = os.path.join(TEX, "RimMandrake", "FlowWorks", "Hose")
GROUND = (126, 112, 92, 255)
VIS = 0.18                      # HoseMath.FlatVisible (flat pose, thickness 1)
FLAT_BAND = 59.0 / 64.0
PIECE_BAND, COUPLING_MAX, JOINER_FACE = 0.25, 0.508, 0.46
WRAP_K, WRAP_LEN, BIND_BAND, WIDEN = 1.3, 0.6, 0.95, 1.5


def hose_tex(look, piece):
    p = os.path.join(HOSE, "Styles", look, piece + ".png") if look in ("Industrial", "Modern", "Futuristic") else None
    if not p or not os.path.exists(p):
        p = os.path.join(HOSE, piece + ".png")
    return Image.open(p).convert("RGBA")


def quad(canvas, tex, centre, d, length, width, world2px, ppc):
    """Paste tex as a quad of length x width cells centred at centre, its +u along unit d (v-up on d's left)."""
    L, W = max(1, int(round(length * ppc))), max(1, int(round(width * ppc)))
    im = tex.resize((L, W), Image.LANCZOS)
    ang = math.degrees(math.atan2(d[1], d[0]))
    im = im.rotate(ang, resample=Image.BICUBIC, expand=True)
    cx, cy = world2px(centre)
    canvas.alpha_composite(im, (int(round(cx - im.width / 2)), int(round(cy - im.height / 2))))


def render(b, look, g, dz_table, geo, ppc, after):
    w, h = b["size"]
    dw, dh = g["drawSize"]
    ox, oz = g["drawOffset"][0], g["drawOffset"][2]
    margin = 2.2
    x0 = min(0.0, w / 2 + ox - dw / 2) - margin
    x1 = max(float(w), w / 2 + ox + dw / 2) + margin
    z0 = min(0.0, h / 2 + oz - dh / 2) - margin
    z1 = max(float(h), h / 2 + oz + dh / 2) + margin
    W, H = int((x1 - x0) * ppc), int((z1 - z0) * ppc)
    can = Image.new("RGBA", (W, H), GROUND)
    w2p = lambda p: ((p[0] - x0) * ppc, (z1 - p[1]) * ppc)
    hlook = look if look in gate.LOOKS else "Scrapper"
    collar, pipe = (Image.open(os.path.join(gate.JOINS, hlook, n + ".png")).convert("RGBA") for n in ("UnderCollar", "UnderPipe"))
    strand, coupling, binding = hose_tex(hlook, "Strand_Flat"), hose_tex(hlook, "Coupling_Bare"), hose_tex(hlook, "Binding")
    seen = set()
    for side, lane, pt in gate.ports(b, look, dz_table):
        if side in seen:
            continue                      # one hose per side
        seen.add(side)
        nx, nz = gate.SIDES[side]
        d = (-nx, -nz)                    # inward: end cell -> fixture
        reach = gate.reach_of(pt, side, b["size"], geo)
        clipped = gate.table_reach(TABLE, b, look, side, pt) if after else None
        if clipped is not None and clipped >= 0:
            reach = clipped
        if after and (clipped is None or clipped >= 0):
            cl, cw, pw = geo
            pl = reach - cl / 2
            quad(can, pipe, (pt[0] + d[0] * (cl / 2 + pl / 2), pt[1] + d[1] * (cl / 2 + pl / 2)), d, pl, pw, w2p, ppc)
            quad(can, collar, (pt[0] + d[0] * cl / 2, pt[1] + d[1] * cl / 2), d, cl, cw, w2p, ppc)
        else:                             # today: the hose ribbon runs on under the fixture to its centre
            quad(can, strand, (pt[0] + d[0] * reach / 2, pt[1] + d[1] * reach / 2), d, reach, VIS / FLAT_BAND, w2p, ppc)
        run = 2.0                         # hose: straight, 2 cells out from the port
        quad(can, strand, (pt[0] - d[0] * run / 2, pt[1] - d[1] * run / 2), d, run, VIS / FLAT_BAND, w2p, ppc)
        size = min(VIS / PIECE_BAND, 0.95 * WRAP_K * VIS / COUPLING_MAX) * WIDEN
        c = (pt[0] - d[0] * JOINER_FACE * size, pt[1] - d[1] * JOINER_FACE * size)
        quad(can, coupling, c, d, size, size, w2p, ppc)
        brass = (c[0] - d[0] * 0.03 * size, c[1] - d[1] * 0.03 * size)
        wc = (brass[0] + d[0] * (0.05 - WRAP_LEN / 2), brass[1] + d[1] * (0.05 - WRAP_LEN / 2))
        quad(can, binding, wc, d, WRAP_LEN, WRAP_K * VIS / BIND_BAND, w2p, ppc)
    fix = Image.open(gate.tex_paths(g["texPath"])[0]).convert("RGBA")
    quad(can, fix, (w / 2 + ox, h / 2 + oz), (1, 0), dw, dh, w2p, ppc)
    return can


def sheet(b, look, g, dz_table, geo):
    tiles = [[render(b, look, g, dz_table, geo, ppc, after) for after in (False, True)] for ppc in (64, 256)]
    gap, head = 16, 22
    W = max(sum(t.width for t in row) + gap for row in tiles)
    H = sum(row[0].height for row in tiles) + gap + head
    out = Image.new("RGBA", (W, H), (36, 36, 36, 255))
    ImageDraw.Draw(out).text((6, 5), "%s %s | left BEFORE (hose stub only), right AFTER (under-coupler beneath the fixture) | "
                             "top game scale 64 px/cell, bottom 4x | offline approximation" % (b["def"], look), fill=(235, 235, 235))
    y = head
    for row in tiles:
        x = 0
        for t in row:
            out.alpha_composite(t, (x, y))
            x += t.width + gap
        y += row[0].height + gap
    return out


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    os.makedirs(argv[1], exist_ok=True)
    dz_table, geo = gate.port_dz_table(), gate.under_geom()
    n = 0
    for b in sorted(gate.load_defs(), key=lambda x: x["def"]):
        for look, g in b["looks"].items():
            name = "%s_%s.png" % (b["def"], look.strip("()"))
            sheet(b, look, g, dz_table, geo).convert("RGB").save(os.path.join(argv[1], name))
            n += 1
    print("wrote %d composites into %s" % (n, argv[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
