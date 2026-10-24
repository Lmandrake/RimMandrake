"""ANCHOR_BASE_REDRAW_STILL_LYING_FLAT A2: rebuild the styled Heavy suspension anchors (Scrapper/Industrial/Modern/
Futuristic, S/E/N) as upright bollards, the same way build_bollards.py did the styled Timber/Steel ones (it reuses that
script's functions). The Heavy bollard is the look's own Steel bollard from bollards_sheet.png on a wider footing; the
ropes are the flat pictures' own rope pixels (styled_heavy_pre_bollard/, frozen copies; positions in
anchor_ropes_pre_bollard.json). Run measure_cable_art.py afterwards and copy the look/Heavy/<facing> table into
RM_DrawbridgeCableMath.Art.

    python3 src/RimMandrake/FlowWorks/art_source/Drawbridge/build_bollards_heavy.py [--out <Textures root>]
"""
import json
import os
import sys

import numpy as np
from PIL import Image

import build_bollards as B

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "styled_heavy_pre_bollard")
HEAVY_WIDTH = 58   # px, wider than the 50 px Timber/Steel bollards: the Heavy tier


def main():
    root = B.TEX
    if "--out" in sys.argv:
        root = sys.argv[sys.argv.index("--out") + 1]
    table = json.load(open(B.OLD))["anchors"]
    B.WIDTH = HEAVY_WIDTH
    bs = B.bollards()   # the look's Steel bollard, at the Heavy width
    out_root = os.path.join(root, "RimMandrake", "FlowWorks", "SuspensionBridge")
    n = 0
    for look in B.LOOKS:
        for f in ("east", "north", "south"):
            name = "RM_SuspensionAnchor_Heavy_%s.png" % f
            old = np.array(Image.open(os.path.join(SRC, look, name)).convert("RGBA"))
            ropes = table["%s/Heavy/%s" % (look, f)]
            canvas = Image.fromarray(np.ascontiguousarray(B.unturn(B.ropes_only(B.turn(old, f), ropes), f)))
            if f == "east":
                strip = B.rope_strip(old, ropes[0])
            post, info = B.wrap(bs[(look, "Steel")], strip)
            feet = sorted((B.ground_xy(f, B.BASE_ALONG, r["lateral"]) for r in ropes), key=lambda p: p[1])
            for gx, gy in feet:
                ox, oy = B.paste(canvas, post, gx, gy)
                w = post.size[0]
                if f == "east":
                    sx, sy = info["side"]
                    canvas = B.strand(canvas, (ox + sx, oy + sy), (gx + w / 2.0 + 2, gy), info["band"] + 1, strip)
                elif f == "south":
                    sx, sy = info["front"]
                    canvas = B.strand(canvas, (ox + sx, oy + sy), (gx, gy + B.FLANGE_HALF * w + 3), info["band"] + 1, strip)
            os.makedirs(os.path.join(out_root, look), exist_ok=True)
            canvas.save(os.path.join(out_root, look, name))
            n += 1
    print("wrote %d pictures under %s" % (n, out_root))


if __name__ == "__main__":
    main()
