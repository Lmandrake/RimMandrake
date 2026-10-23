"""ANCHOR_BASE_REDRAW_STILL_LYING_FLAT: rebuild the unstyled suspension anchors (base Rope/Timber/Steel/Heavy) as upright
bollards, Graphic_Multi _south/_east/_north, exactly the way build_bollards.py did the styled Timber/Steel ones (it
reuses that script's functions): one bollard per material (bollards_base_sheet.png, codex image_gen, 4 in a row) pasted
at each rope's line; the ropes are the old single picture's own rope pixels (art_source/Drawbridge/base_pre_bollard/).
Run measure_cable_art.py afterwards and copy its base/<M>/<facing> table into RM_DrawbridgeCableMath.Art.

    python3 src/RimMandrake/FlowWorks/art_source/Drawbridge/build_bollards_base.py [--out <Textures root>]
"""
import json
import os
import sys

import numpy as np
from PIL import Image

import build_bollards as B

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = os.path.join(HERE, "bollards_base_sheet.png")
OLD = os.path.join(HERE, "anchor_ropes_pre_bollard_base.json")
SRC = os.path.join(HERE, "base_pre_bollard")
MATS = ["Rope", "Timber", "Steel", "Heavy"]
WIDTHS = {"Rope": 44, "Timber": 50, "Steel": 50, "Heavy": 58}   # px; the Heavy footing is wider than its post


def bollards():
    a = np.array(Image.open(SHEET).convert("RGBA"))
    m = a[:, :, 3] > 40
    h, w = m.shape
    out = {}
    occ = m.any(0)
    spans, x = [], 0
    while x < w:   # the bollards are the four runs of occupied columns (neighbouring ones overlap the equal quarters)
        if occ[x]:
            x1 = x
            while x1 < w and occ[x1]:
                x1 += 1
            spans.append((x, x1))
            x = x1
        else:
            x += 1
    spans = [sp for sp in spans if sp[1] - sp[0] > 20]
    assert len(spans) == len(MATS), spans
    for col, mat in enumerate(MATS):
        x0, x1 = spans[col]
        ys, xs = np.where(m[:, x0:x1])
        crop = Image.fromarray(a[ys.min(): ys.max() + 1, x0 + xs.min(): x0 + xs.max() + 1])
        img = crop.resize((WIDTHS[mat], max(1, round(crop.height * WIDTHS[mat] / float(crop.width)))), Image.LANCZOS)
        arr = np.array(img)
        arr[arr[:, :, 3] < 10] = 0
        out[mat] = Image.fromarray(arr)
    return out


def main():
    root = os.path.join(HERE, "..", "..", "Textures")
    if "--out" in sys.argv:
        root = sys.argv[sys.argv.index("--out") + 1]
    table = json.load(open(OLD))["anchors"]
    bs = bollards()
    out_dir = os.path.join(root, "Things", "Building", "FlowWorks", "SuspensionBridge")
    os.makedirs(out_dir, exist_ok=True)
    for mat in MATS:
        ropes = table["base/%s/single" % mat]
        single = np.array(Image.open(os.path.join(SRC, "RM_SuspensionAnchor_%s.png" % mat)).convert("RGBA"))
        east_frame = B.turn(single, "north")   # the single is drawn north-up: turn it so the ropes run +x
        strip = B.rope_strip(east_frame, ropes[0])
        for f in ("east", "north", "south"):
            canvas = Image.fromarray(np.ascontiguousarray(B.unturn(B.ropes_only(east_frame, ropes), f)))
            post, info = B.wrap(bs[mat], strip)
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
            canvas.save(os.path.join(out_dir, "RM_SuspensionAnchor_%s_%s.png" % (mat, f)))
    print("wrote 12 pictures under", out_dir)


if __name__ == "__main__":
    main()
