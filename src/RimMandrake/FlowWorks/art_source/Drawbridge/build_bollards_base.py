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
WIDTHS = {"Rope": 44, "Timber": 50, "Steel": 50, "Heavy": 62}   # px; the Heavy footing is wider than its post


def round_plinth(crop):
    """The sheet's Heavy bollard stands on an ISOMETRIC square slab (a diamond with a pointed front corner), which the
    orthographic ~35 deg building camera never shows (judge 2026-10-23): keep its post and concrete texture, drop the
    slab, and stand the post on a round concrete disc like every other bollard (ellipse ratio 0.56, FLANGE_HALF)."""
    a = np.array(crop).astype(np.float32)
    al = a[:, :, 3] > 40
    h, w = al.shape
    widths = al.sum(1)
    rows = np.where(al.any(1))[0]
    mid = int(rows.min() + 0.57 * (rows.max() - rows.min()))     # the bare post below the iron band
    cols = np.where(al[mid])[0]
    cx = (cols.min() + cols.max()) / 2.0
    body = float(widths[mid])
    cut = next(y for y in range(mid, h) if widths[y] > body * 1.05)    # the row the slab begins to widen past the post
    # concrete texture: a patch of the bare post, mirrored out so it tiles without seams
    patch = a[mid - 60: mid + 20, int(cx - body * 0.4): int(cx + body * 0.4)]
    tex = np.concatenate([patch, patch[:, ::-1]], 1)
    tex = np.concatenate([tex, tex[::-1]], 0)
    # the sheet's Heavy post is stubby (1:1); lengthen the bare shaft below the iron band to the 2:1 of the other bollards
    seg0 = next(y for y in range(int(np.argmax(widths[:mid])), h) if widths[y] <= body * 1.01) + 2   # just below the band
    seg = Image.fromarray(a[seg0:cut].astype(np.uint8)).resize((w, (cut - seg0) + 300), Image.LANCZOS)
    a = np.concatenate([a[:seg0], np.array(seg).astype(np.float32), a[cut:]], 0)
    extra = seg.height - (cut - seg0)
    cut += extra
    mid = seg0 + (cut - seg0) // 2
    h = a.shape[0]
    th, tw = tex.shape[:2]
    rx = body * 0.72
    ry = 0.56 * rx
    thick = 0.30 * rx
    yc = cut - 0.56 * body / 2.0                         # the post's foot: centre of the disc's top ellipse
    H = int(np.ceil(yc + thick + ry + 6))
    W = int(np.ceil(2 * rx + 8))
    ox = W / 2.0
    out = np.zeros((H, W, 4), np.float32)
    ys, xs = np.mgrid[0:H, 0:W]
    top = ((xs - ox) / rx) ** 2 + ((ys - yc) / ry) ** 2 <= 1
    bot = ((xs - ox) / rx) ** 2 + ((ys - (yc + thick)) / ry) ** 2 <= 1
    side = (np.abs(xs - ox) <= rx) & (ys >= yc) & (ys <= yc + thick)
    disc = top | bot | side
    sampled = tex[(ys % th), (xs % tw)]
    out[disc] = sampled[disc]
    out[disc, 3] = 255
    out[(disc & ~top)][:, :3] *= 1.0
    shade = np.where(top, 1.0, 0.72)
    out[:, :, :3] *= shade[:, :, None]
    # post: the original rows above the cut, then its own front arc down to the disc's top face
    px0 = int(round(cx - ox))
    post = np.zeros((H, W, 4), np.float32)
    pr = body / 2.0
    prb = 0.56 * pr
    for y in range(min(int(cut) + 1, h)):
        for x in range(W):
            sx = x + px0
            if not (0 <= sx < w and a[y, sx, 3] > 40):
                continue
            u = (x - ox) / pr
            if y > yc and (abs(u) >= 1 or y > yc + prb * np.sqrt(1 - u * u)):
                continue   # below the post's own front arc
            post[y, x] = a[y, sx]
    # the post's front arc as a dark line where it meets the disc
    for x in range(W):
        u = (x - ox) / pr
        if abs(u) < 1:
            yb = int(yc + prb * np.sqrt(1 - u * u))
            for d in (0, 1, 2):
                if 0 <= yb + d < H:
                    post[yb + d - 1, x] = [22, 22, 22, 255]
    # dark outline round the disc
    edge = disc & ~(np.roll(disc, 1, 0) & np.roll(disc, -1, 0) & np.roll(disc, 1, 1) & np.roll(disc, -1, 1))
    for _ in range(2):
        edge = edge | (np.roll(edge, 1, 0) & disc) | (np.roll(edge, 1, 1) & disc)
    out[edge, :3] = 22
    # a contact line where the post meets the top face, then the post over the disc
    m = post[:, :, 3] > 40
    out[m] = post[m]
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


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
        if mat == "Heavy":
            crop = round_plinth(crop)
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
