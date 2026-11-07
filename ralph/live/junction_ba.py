#!/usr/bin/env python3
"""Junctions before and after, side by side at play zoom, from two colony_scene runs. Runs here on fetched shots, no game.

    python3 ralph/live/junction_ba.py SHOTS_DIR PRE_TAG NOW_TAG OUT_TAG [Look ...]

One sheet per look and frame: the pre-pass-1 build on the left, today's on the right, unscaled.
"""
import os, sys
from PIL import Image, ImageDraw

d, pre, now, out = sys.argv[1:5]
looks = sys.argv[5:] or ["Scrapper", "Industrial", "Modern", "Futuristic"]
for look in looks:
    for frame in ("house", "yard"):
        a = os.path.join(d, "%s_%s_%s.png" % (pre, look, frame))
        b = os.path.join(d, "%s_%s_%s.png" % (now, look, frame))
        if not (os.path.exists(a) and os.path.exists(b)):
            print("missing", a if not os.path.exists(a) else b)
            continue
        A, B = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
        S = Image.new("RGB", (A.size[0] + B.size[0] + 12, max(A.size[1], B.size[1]) + 26), (20, 20, 20))
        S.paste(A, (0, 26))
        S.paste(B, (A.size[0] + 12, 26))
        dr = ImageDraw.Draw(S)
        dr.text((8, 7), "BEFORE: the pre-pass-1 build, 903ba19f (%s, %s)" % (look, frame), fill=(255, 255, 255))
        dr.text((A.size[0] + 20, 7), "NOW", fill=(255, 255, 255))
        name = "%s_%s_%s.png" % (out, look, frame)
        S.save(os.path.join(d, name))
        print(name, S.size)
