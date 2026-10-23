#!/usr/bin/env python3
"""Offline mock (NOT in-game) of a lying hose: coupling end on the left, bare free end (Binding wrap + Mouth) on the right,
sized from HoseMath (FlatVisible 0.18, WrapLength 0.6, WrapK 1.3, Mouth 0.30 x 0.86 vis, CouplingMax/PieceBand fitting size).
Usage: hose_end_mock.py OUT.png LOOK_DIR [--px 128]"""
import argparse
from pathlib import Path
from PIL import Image
ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("look"); ap.add_argument("--px", type=int, default=128)
a = ap.parse_args(); px = a.px; L = Path(a.look)
vis = 0.18; W, H = 5, 1.4
im = Image.new("RGBA", (int(W * px), int(H * px)), (112, 86, 62, 255)); cy = H / 2
def put(img, cx, sx, sy):
    t = img.convert("RGBA").resize((max(1, int(sx * px)), max(1, int(sy * px))), Image.LANCZOS)
    im.alpha_composite(t, (int(cx * px - t.width / 2), int(cy * px - t.height / 2)))
strand = Image.open(L / "Strand_Flat.png") if (L / "Strand_Flat.png").exists() else Image.open(L.parent.parent / "Strand_Flat.png")
x0, x1 = 0.9, 4.3
put(strand, (x0 + x1) / 2, x1 - x0, vis / (59 / 64))
size = min(vis / 0.25, 0.95 * 1.3 * vis / 0.508)          # FittingSize
put(Image.open(L / "Coupling_Bare.png").transpose(Image.FLIP_LEFT_RIGHT), x0 - 0.0, size, size)
put(Image.open(L / "Binding.png"), x1 - (0.6 / 2 - 0.02), 0.6, 1.3 * vis / 0.95)
put(Image.open(L / "Mouth.png"), x1 - 0.10 * vis, 0.30 * vis, 0.86 * vis)
im.convert("RGB").save(a.out); print(a.out)
