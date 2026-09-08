#!/usr/bin/env python3
"""
make_complex_structures_icon.py — the world-map icon for RUT_ComplexStructures.

Owner, 2026-09-07: he wanted a marker that "clearly identified complex structures...
indicating a particularly complicated and dense network on the map".

WHY PROCEDURAL. Local image generation is PARKED by owner ruling (2026-09-05) and the
Codex path pops an interactive Windows UAC dialog that must not fire unattended. This
draws the icon deterministically instead, matching the house style measured off the
existing sheets in Textures/World/Landmarks/Ashkarr/:

    1024x1024 RGBA, a 2x2 grid of FOUR variants at 512x512 each
    chunky near-black outline, flat fills, grey palette with brown accents
    shapes sit off-centre and rotate a little so the four read as different places

The subject is a NETWORK, not a building: blocks joined by conduits, with satellite
nodes hanging off the trunk. That is what distinguishes it from Ruins (rubble) and
AncientGarrison (one compound) — this icon has to say "many things, wired together".

Deterministic: layout comes from a fixed table, never RNG, so a re-run reproduces the
same icon and there is no seed that could roll a different one.

    python3 make_complex_structures_icon.py            # writes the PNG
"""
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Textures", "World", "Landmarks", "Ashkarr",
                   "RUT_ComplexStructures.png")

CELL = 512
OUTLINE = (38, 36, 34, 255)
GREYS = [(176, 176, 176, 255), (146, 148, 150, 255), (116, 118, 120, 255),
         (86, 88, 90, 255), (196, 196, 194, 255)]
BROWN = (138, 106, 74, 255)
W = 9                                   # outline weight, matched to the sheets

# Four variants. Each is (nodes, links). A node is (cx, cy, w, h, colour index,
# accent?) in cell coordinates; a link is a pair of node indices.
VARIANTS = [
    ([(150, 150, 130, 110, 1, 0), (330, 130, 90, 90, 3, 1), (250, 300, 150, 120, 2, 0),
      (400, 320, 80, 70, 0, 0), (120, 360, 70, 70, 4, 0), (370, 200, 50, 46, 3, 0)],
     [(0, 1), (0, 2), (2, 3), (2, 4), (1, 5), (5, 3)]),
    ([(260, 120, 160, 100, 2, 0), (140, 260, 100, 110, 0, 1), (330, 300, 120, 130, 1, 0),
      (180, 400, 80, 66, 3, 0), (400, 160, 60, 60, 4, 0), (250, 250, 46, 46, 3, 0)],
     [(0, 1), (0, 2), (1, 3), (3, 2), (0, 4), (1, 5), (5, 2)]),
    ([(160, 200, 120, 130, 3, 0), (320, 160, 110, 90, 1, 0), (300, 340, 140, 100, 0, 1),
      (110, 370, 66, 66, 2, 0), (420, 250, 70, 80, 4, 0), (230, 100, 56, 50, 2, 0)],
     [(0, 1), (1, 4), (4, 2), (0, 2), (0, 3), (1, 5)]),
    ([(230, 180, 150, 140, 0, 0), (390, 140, 80, 76, 2, 0), (150, 340, 96, 90, 1, 1),
      (330, 350, 100, 90, 3, 0), (420, 300, 56, 56, 4, 0), (120, 180, 56, 60, 3, 0)],
     [(0, 1), (0, 2), (0, 3), (3, 4), (2, 3), (5, 0)]),
]


def draw_variant(d, ox, oy, nodes, links):
    # conduits first, so blocks sit on top of them
    for a, b in links:
        ax, ay = nodes[a][0] + ox, nodes[a][1] + oy
        bx, by = nodes[b][0] + ox, nodes[b][1] + oy
        d.line([(ax, ay), (bx, by)], fill=OUTLINE, width=W * 4)
    for a, b in links:
        ax, ay = nodes[a][0] + ox, nodes[a][1] + oy
        bx, by = nodes[b][0] + ox, nodes[b][1] + oy
        d.line([(ax, ay), (bx, by)], fill=GREYS[2], width=W * 2)
    for (cx, cy, w, h, ci, accent) in nodes:
        x0, y0 = ox + cx - w // 2, oy + cy - h // 2
        x1, y1 = x0 + w, y0 + h
        d.rectangle([x0, y0, x1, y1], fill=GREYS[ci], outline=OUTLINE, width=W)
        # internal division lines: the "complicated" reading
        d.line([(x0 + w // 2, y0), (x0 + w // 2, y1)], fill=OUTLINE, width=max(3, W // 2))
        d.line([(x0, y0 + h // 2), (x1, y0 + h // 2)], fill=OUTLINE, width=max(3, W // 2))
        if w > 90:
            d.line([(x0 + w // 4, y0), (x0 + w // 4, y1)], fill=OUTLINE, width=max(2, W // 3))
        if accent:
            d.rectangle([x0 + w // 2, y0 + h // 2, x1 - W, y1 - W], fill=BROWN,
                        outline=OUTLINE, width=max(2, W // 3))


def main():
    img = Image.new("RGBA", (CELL * 2, CELL * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, (nodes, links) in enumerate(VARIANTS):
        ox, oy = (i % 2) * CELL, (i // 2) * CELL
        draw_variant(d, ox, oy, nodes, links)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT)
    print("wrote %s  %s" % (OUT, img.size))


if __name__ == "__main__":
    main()
