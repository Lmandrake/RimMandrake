#!/usr/bin/env python3
"""Offline mock (NOT in-game) of hose joins as RM_MapComponent_Hoses.DrawEnds draws them, at game geometry:
a mid-hose joiner (two Coupling_Bare halves face to face, HoseMath.JoinerMesh 0.33, wraps at JoinerWrapIn 0.09) and an
end coupling meeting a port (Fitting: centre -JoinerFace x size behind the face, wrap from brass -0.03), each pointing
east, north, west and south. Piece() maps the texture's +X onto the direction (Quaternion.Euler(0,-ang,0)).
Sizes: FlatVisible 0.18, FittingSize = min(vis/0.25, 0.95*1.3*vis/0.508), WrapLength 0.6, wrap width 1.3*vis/0.95.
Usage: render_joins.py OUT.png [--look DIR ...] [--px 96]   (one row per look dir; default: the four shipped looks)"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw

HOSE = Path(__file__).resolve().parents[2] / "Textures/RimMandrake/FlowWorks/Hose"
LOOKS = [HOSE, HOSE / "Styles/Industrial", HOSE / "Styles/Modern", HOSE / "Styles/Futuristic"]
VIS = 0.18
SIZE = min(VIS / 0.25, 0.95 * 1.3 * VIS / 0.508)
DIRS = {"E": (1, 0), "N": (0, 1), "W": (-1, 0), "S": (0, -1)}
ROT = {"E": 0, "N": 90, "W": 180, "S": -90}          # PIL rotate is CCW; world north is image up


def piece(canvas, px, img, cx, cz, d, sx, sz):
    """Draw img (texture +X along d) centred at world (cx, cz) in cell units, scaled sx along d, sz across."""
    t = img.resize((max(1, round(sx * px)), max(1, round(sz * px))), Image.LANCZOS).rotate(ROT[d], expand=True)
    canvas.alpha_composite(t, (round(cx * px - t.width / 2), round(canvas.height - cz * px - t.height / 2)))


def find(look, name):
    p = look / name
    return p if p.exists() else HOSE / name


def scene(look, px):
    cpl = Image.open(look / "Coupling_Bare.png").convert("RGBA")
    bind = Image.open(find(look, "Binding.png")).convert("RGBA")
    strand = Image.open(find(look, "Strand_Flat.png")).convert("RGBA")
    W, H = 8 * 1.6, 2 * 1.6
    im = Image.new("RGBA", (round(W * px), round(H * px)), (116, 98, 70, 255))
    ww = 1.3 * VIS / 0.95
    for k, (name, (dx, dz)) in enumerate(DIRS.items()):
        # joiner at (jx, jz) with the run along d (each half points at the joint along +-d)
        jx, jz = 0.8 + k * 1.6, 2.4
        piece(im, px, strand, jx, jz, name, 1.5, VIS / (59 / 64))
        for half, h in ((0, name), (1, {"E": "W", "W": "E", "N": "S", "S": "N"}[name])):
            hx, hz = DIRS[h]
            piece(im, px, cpl, jx - hx * 0.33 * SIZE, jz - hz * 0.33 * SIZE, h, SIZE, SIZE)
        for h in (name, {"E": "W", "W": "E", "N": "S", "S": "N"}[name]):
            hx, hz = DIRS[h]
            o = 0.09 * SIZE + 0.3
            piece(im, px, bind, jx - hx * o, jz - hz * o, h, 0.6, ww)
        # end coupling: face at a port edge, hose coming from behind (-d)
        fz = 0.8
        fx = 0.8 + k * 1.6 + 6.4
        piece(im, px, strand, fx - dx * 0.75, fz - dz * 0.75, name, 1.5, VIS / (59 / 64))
        c = (fx - dx * 0.46 * SIZE, fz - dz * 0.46 * SIZE)
        piece(im, px, cpl, c[0], c[1], name, SIZE, SIZE)
        b = (c[0] - dx * 0.03 * SIZE, c[1] - dz * 0.03 * SIZE)
        piece(im, px, bind, b[0] + dx * (0.05 - 0.3), b[1] + dz * (0.05 - 0.3), name, 0.6, ww)
    dr = ImageDraw.Draw(im)
    dr.text((4, 4), f"{look.name}: joiners E N W S (top) | port couplings E N W S (bottom right)", fill=(255, 255, 255, 255))
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--look", action="append")
    ap.add_argument("--px", type=int, default=96)
    a = ap.parse_args()
    looks = [Path(p) for p in a.look] if a.look else LOOKS
    rows = [scene(l, a.px) for l in looks]
    out = Image.new("RGBA", (rows[0].width, sum(r.height for r in rows)))
    y = 0
    for r in rows:
        out.alpha_composite(r, (0, y)); y += r.height
    out.convert("RGB").save(a.out)
    print(a.out, out.size)


if __name__ == "__main__":
    main()
