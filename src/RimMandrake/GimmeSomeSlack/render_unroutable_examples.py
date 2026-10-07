#!/usr/bin/env python3
"""Render the A7 unroutable census (SelfTest/UnroutableCensus.cs) as small top-down diagrams.

    python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py --no-export --unroutable-census OUT/census.json 200
    python3 src/RimMandrake/GimmeSomeSlack/render_unroutable_examples.py OUT/census.json OUT/

One PNG per constructed scene plus the first vanilla-base example of each class. Legend: brown wall, grey rock, blue water,
tan box = a building footprint (powered ones carry a label), orange line = conduit (dark orange = buried under a wall or
water), black curve = the cord as the builder draws it today, dashed red = the unroutable leg's straight line, red hatch =
the blocked cells that line crosses.
"""
import json
import os
import re
import sys

from PIL import Image, ImageDraw

CS = 26
PAD = 8
TOP = 44
COL = {".": (226, 214, 190), "W": (92, 62, 40), "R": (128, 124, 118), "w": (70, 120, 180), "D": (196, 170, 120), "|": (160, 110, 60)}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:60]


def render(c, path, title):
    W, H = c["w"], c["h"]
    img = Image.new("RGB", (W * CS + 2 * PAD, H * CS + 2 * PAD + TOP), (40, 30, 24))
    dr = ImageDraw.Draw(img)

    def px(x, z):  # world (cells, z up) -> image
        return PAD + x * CS, TOP + PAD + (H - z) * CS

    rows = c["rows"]
    cond = set()
    for z, row in enumerate(rows):
        for x in range(W):
            ch, cd = row[2 * x], row[2 * x + 1]
            x0, y1 = px(x, z)
            dr.rectangle([x0, y1 - CS, x0 + CS - 1, y1 - 1], fill=COL.get(ch, COL["."]), outline=(200, 188, 164) if ch == "." else None)
            if cd == "+":
                cond.add((x, z))
    for (x0, z0) in [tuple(q) for q in c["crossed"]]:
        a, b = px(x0, z0)
        for k in range(-CS, CS, 6):
            dr.line([a + max(0, k), b - max(0, -k), a + min(CS, CS + k), b - min(CS, CS - k)], fill=(220, 40, 40), width=1)
    for (x, z) in cond:  # conduit: a line to each conduit neighbour; buried cells drawn darker
        ch = rows[z][2 * x]
        colr = (230, 140, 30) if ch in ".|" else (150, 80, 10)
        cx, cy = px(x + 0.5, z + 0.5)
        for dx, dz in ((1, 0), (0, 1)):
            if (x + dx, z + dz) in cond:
                nx, ny = px(x + dx + 0.5, z + dz + 0.5)
                dr.line([cx, cy, nx, ny], fill=colr, width=4)
        dr.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=colr)
    for m in c["machines"]:
        a, b = px(m["x"], m["z"])
        dr.rectangle([a + 2, b - m["h"] * CS + 2, a + m["w"] * CS - 3, b - 3], fill=(240, 220, 140), outline=(30, 20, 10), width=2)
        dr.text((a + 4, b - m["h"] * CS + 4), m["id"][:5], fill=(30, 20, 10))
    for st in c["strands"]:
        pts = [px(st[i], st[i + 1]) for i in range(0, len(st) - 1, 2)]
        if len(pts) > 1:
            dr.line(pts, fill=(15, 15, 15), width=3)
    if c.get("leg") and c["class"] != "routable":
        (x0, y0), (x1, y1) = px(c["leg"][0], c["leg"][1]), px(c["leg"][2], c["leg"][3])
        n = 24
        for i in range(0, n, 2):
            dr.line([x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n, x0 + (x1 - x0) * (i + 1) / n, y0 + (y1 - y0) * (i + 1) / n], fill=(230, 30, 30), width=2)
    dr.text((PAD, 6), title, fill=(245, 230, 200))
    dr.text((PAD, 22), "class " + c["class"] + ("  crosses: " + c["detail"] if c["detail"] else ""), fill=(245, 200, 150))
    img.save(path)


def main(src, out):
    d = json.load(open(src))
    os.makedirs(out, exist_ok=True)
    written = []
    for c in d["cases"]:
        if not c["source"][0].isdigit():
            continue
        p = os.path.join(out, "constructed_" + slug(c["source"]) + ".png")
        render(c, p, c["source"])
        written.append(p)
    seen = set()
    for c in d["cases"]:
        if not c["source"].startswith("vanilla base") or c["class"] in seen:
            continue
        seen.add(c["class"])
        p = os.path.join(out, "vanilla_" + slug(c["class"]) + "_" + slug(c["source"]) + ".png")
        render(c, p, c["source"] + " (random base, vanilla hookup rule)")
        written.append(p)
    for p in written:
        print(p)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
