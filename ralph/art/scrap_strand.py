#!/usr/bin/env python3
"""Scrapper's floor cord, "rough, hacked-together, crude" (style design): Strand_Jawa's own jacket, a length of salvaged rust-red cable
spliced in and a short patch of faded olive cable, silver duct tape and cream electrical tape at the joints, unevenly spaced. 1024x32,
so with the ribbon's repeat taken from the texture's aspect it repeats every 2.56 cells instead of 0.32 (eight Jawa tiles' worth of
texels), long enough that a cord does not read as evenly striped.
    python3 ralph/art/scrap_strand.py OUT.png [preview.png]"""
import random, sys
from PIL import Image

SRC = "src/RimMandrake/GimmeSomeSlack/Textures/RimMandrake/GimmeSomeSlack/Strand_Jawa.png"
W, H = 1024, 32
rnd = random.Random(1709)
jawa = Image.open(SRC).convert("RGBA")
out = Image.new("RGBA", (W, H))
for x in range(W):
    for y in range(H):
        out.putpixel((x, y), jawa.getpixel((x % 128, y)))


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def jacket(x0, x1, c0, c1, c2):
    """A length of another salvaged cable: the same jacket shading in that cable's colour, scuffed in blotches."""
    blot = {}
    for x in range(x0, x1):
        for y in range(H):
            r, g, b, a = jawa.getpixel((x % 128, y))
            if a == 0:
                continue
            t = min(1.0, (0.299 * r + 0.587 * g + 0.114 * b) / 62.0)
            c = lerp(c0, c1, t) if t < 0.85 else lerp(c1, c2, (t - 0.85) / 0.15)
            k = blot.setdefault((x // 7, y // 5), 0.82 + 0.3 * rnd.random())
            out.putpixel((x, y), tuple(max(0, min(255, int(v * k))) for v in c) + (a,))


jacket(344, 520, (40, 18, 11), (138, 62, 33), (182, 104, 64))     # rust-red
jacket(790, 862, (30, 32, 16), (92, 96, 52), (132, 136, 84))       # faded olive


def tape(x0, x1, base, hi, lo, seam):
    """A wrap of tape round the cord: a little proud of it, ragged at its edges, the spiral overlap showing as faint diagonals."""
    edge0 = [x0 + rnd.randint(-2, 1) for _ in range(H)]
    edge1 = [x1 + rnd.randint(-1, 2) for _ in range(H)]
    for y in range(2, 29):
        v = (y - 2) / 26.0
        c = lerp(hi, base, min(1, abs(v - 0.3) / 0.3)) if v < 0.6 else lerp(base, lo, (v - 0.6) / 0.4)
        for x in range(edge0[y], edge1[y]):
            cc = c
            if (x - x0 + y // 2) % 13 == 0:
                cc = lerp(c, seam, 0.6)
            if y in (2, 28) or x in (edge0[y], edge1[y] - 1):
                cc = lerp(cc, (12, 10, 9), 0.55)
            k = 0.93 + 0.12 * rnd.random()
            out.putpixel((x % W, y), tuple(max(0, min(255, int(q * k))) for q in cc) + ((200 if y in (2, 28) else 255),))


GREY = ((150, 150, 144), (214, 214, 206), (78, 78, 74), (96, 96, 92))
CREAM = ((196, 176, 120), (236, 222, 170), (104, 90, 58), (130, 114, 74))
tape(300, 344, *GREY)     # duct tape at the splice into the rust cable
tape(520, 546, *CREAM)    # electrical tape at the splice out of it
tape(764, 792, *GREY)     # the olive patch, taped in at both ends
tape(860, 884, *CREAM)
out.save(sys.argv[1])

if len(sys.argv) > 2:   # how it reads at play zoom (64 px a cell, strand 0.08 cell wide), beside Industrial's black rubber and ribbed
    bg = Image.new("RGB", (430, 70), (110, 82, 58))
    for row, (path, cells) in enumerate(((sys.argv[1], 2.56), ("src/RimMandrake/GimmeSomeSlack/Textures/RimMandrake/GimmeSomeSlack/Styles/StarWars/Strand_BlackRubber.png", 0.32),
                                         ("src/RimMandrake/GimmeSomeSlack/Textures/RimMandrake/GimmeSomeSlack/Styles/StarWars/Strand_CoiledBlack.png", 0.32),
                                         (SRC, 0.32))):
        t = Image.open(path).convert("RGBA").resize((max(1, round(cells * 64)), 6), Image.LANCZOS)
        for x in range(10, 420, t.size[0]):
            bg.paste(t, (x, 8 + row * 15), t)
    bg.resize((bg.size[0] * 3, bg.size[1] * 3), Image.NEAREST).save(sys.argv[2])
