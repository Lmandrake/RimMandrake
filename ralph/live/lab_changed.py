#!/usr/bin/env python3
"""Every cord two lab lays disagree on, before | after, cropped round the cord, on one sheet per look. Runs here, no game.
    python3 ralph/live/lab_changed.py BEFORE_DIR AFTER_DIR OUT_PREFIX [--looks Modern,...] [--ppc 36] [--cols 4]
Writes OUT_PREFIX_<Look>.png and prints the changed pieces.
"""
import argparse, json, math, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument("before"); ap.add_argument("after"); ap.add_argument("out")
ap.add_argument("--looks", default="Modern,Scrapper,Industrial,Futuristic")
ap.add_argument("--ppc", type=int, default=36)
ap.add_argument("--cols", type=int, default=4)
ap.add_argument("--only", default="", help="substring a piece name must contain")
a = ap.parse_args()
here = os.path.dirname(os.path.abspath(__file__))


def key(p):
    return p["a"] + "|" + p["b"]


for look in a.looks.split(","):
    B = {key(p): p for p in json.load(open(os.path.join(a.before, "ba_%s.out.json" % look)))["pieces"]}
    A = {key(p): p for p in json.load(open(os.path.join(a.after, "ba_%s.out.json" % look)))["pieces"]}
    changed = []
    for k, p in A.items():
        q = B.get(k)
        if a.only and a.only not in k:
            continue
        if q is None or len(q["strands"]) != len(p["strands"]) or any(
                len(s1) != len(s2) or any(math.dist(u, v) > 0.02 for u, v in zip(s1, s2)) for s1, s2 in zip(q["strands"], p["strands"])):
            changed.append(k)
    print(look, len(changed), "changed")
    tiles = []
    with tempfile.TemporaryDirectory() as td:
        for i, k in enumerate(changed):
            pts = [u for s in A[k]["strands"] for u in s] + ([u for s in B[k]["strands"] for u in s] if k in B else [])
            if not pts:
                continue
            x0 = math.floor(min(u[0] for u in pts)) - 1; x1 = math.ceil(max(u[0] for u in pts)) + 1
            z0 = math.floor(min(u[1] for u in pts)) - 1; z1 = math.ceil(max(u[1] for u in pts)) + 1
            w, h = max(x1 - x0, 5), max(z1 - z0, 4)
            if w > 14 or h > 10:
                print("  big", k, w, h)
                w, h = min(w, 14), min(h, 10)
            rect = "%d,%d,%d,%d" % (x0, z0, w, h)
            pair = []
            for j, d in enumerate((a.before, a.after)):
                o = os.path.join(td, "%d_%d.png" % (i, j))
                subprocess.run([sys.executable, os.path.join(here, "lab_render.py"), "Transient/lab/ba/worlds/ba_%s.json" % look,
                                os.path.join(d, "ba_%s.out.json" % look), o, rect, "--ppc", str(a.ppc)], check=True, capture_output=True)
                im = Image.open(o).convert("RGB")
                im.thumbnail((14 * a.ppc, 10 * a.ppc))
                pair.append(im)
            tw = pair[0].width + pair[1].width + 6; th = max(pair[0].height, pair[1].height) + 16
            t = Image.new("RGB", (tw, th), (0, 0, 0))
            t.paste(pair[0], (0, 16)); t.paste(pair[1], (pair[0].width + 6, 16))
            ImageDraw.Draw(t).text((2, 2), "%d %s" % (i, k), fill=(255, 255, 0))
            tiles.append(t)
            print("  %d %s %s" % (i, k, rect))
    if not tiles:
        continue
    cols = a.cols
    rows = [tiles[i:i + cols] for i in range(0, len(tiles), cols)]
    W = max(sum(t.width + 8 for t in r) for r in rows); H = sum(max(t.height for t in r) + 8 for r in rows)
    sheet = Image.new("RGB", (W, H), (30, 30, 30)); y = 0
    for r in rows:
        x = 0
        for t in r:
            sheet.paste(t, (x, y)); x += t.width + 8
        y += max(t.height for t in r) + 8
    out = "%s_%s.png" % (a.out, look)
    sheet.save(out); print(out, sheet.size)
