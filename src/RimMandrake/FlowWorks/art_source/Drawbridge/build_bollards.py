"""ANCHOR_BOLLARD_REDRAW_LIES_DOWN_ON_DUTY: rebuild the styled Timber/Steel suspension-anchor pictures (S/E/N) as upright
bollards seen from the building camera, keeping each picture's own painted ropes,
wound twice round the post above its flange (art-eval DESC_MISS: "no visible wrap or fastening on the upright shafts").

Owner by card 2026-10-23: "Redraw the anchors as upright bollards? -> Redraw, I'll judge after (Recommended)".

An upright round post looks the same from every side, so ONE bollard per look x material (bollards_sheet.png, codex
image_gen, 4 looks x {Timber, Steel}) is pasted into all three facings, standing at the rope's line; the ropes are the old
picture's own rope pixels (from the old attachment point to the painted end, unchanged) tiled back to the bollard's foot.
Occlusion follows the camera: the post is in front of the rope that runs north (away), the rope runs out from under the
flange toward the viewer (south) and sideways (east). The attachment point therefore differs per facing: run
measure_cable_art.py afterwards and copy its table into RM_DrawbridgeCableMath.Art (per-facing keys).

    python3 src/RimMandrake/FlowWorks/art_source/Drawbridge/build_bollards.py [--out <Textures root>]
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "..", "..", "Textures")
SHEET = os.path.join(HERE, "bollards_sheet.png")
OLD = os.path.join(HERE, "anchor_ropes_pre_bollard.json")   # the rope bands measured on the pre-bollard art (frozen)
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
MATS = ["Timber", "Steel"]
N = 256
WIDTH = 50          # bollard width in px (0.2 cell): its cap clears the canvas top over the upper rope (east)
BASE_ALONG = 0.32   # the bollard's foot, as a fraction of the cell from the back edge
FLANGE_HALF = 0.28  # the flange's ground ellipse half-height / width (0.56 / 2)


def bollards():
    a = np.array(Image.open(SHEET).convert("RGBA"))
    m = a[:, :, 3] > 40
    h, w = m.shape
    out = {}
    for row, mat in enumerate(MATS):
        for col, look in enumerate(LOOKS):
            y0, y1 = row * h // 2, (row + 1) * h // 2
            x0, x1 = col * w // 4, (col + 1) * w // 4
            sub = m[y0:y1, x0:x1]
            ys, xs = np.where(sub)
            crop = Image.fromarray(a[y0 + ys.min(): y0 + ys.max() + 1, x0 + xs.min(): x0 + xs.max() + 1])
            sc = WIDTH / float(crop.width)
            img = crop.resize((WIDTH, max(1, round(crop.height * sc))), Image.LANCZOS)
            arr = np.array(img)
            arr[arr[:, :, 3] < 10] = 0
            out[(look, mat)] = Image.fromarray(arr)
    return out


def rope_strip(old_east, r):
    """A straight piece of the picture's own rope (east frame: running along x), tight to its painted rows."""
    c = N / 2.0 - r["lateral"] * N - 0.5
    half = r["thick"] * N / 2.0
    r0, r1 = int(round(c - half)), int(round(c + half)) + 1
    x0 = int(np.ceil(r["attach"] * N)) + 4
    return old_east[r0:r1, x0:x0 + 64].copy()


def wrap(sprite, strip, turns=2, band=6):
    """The rope wound round the post just above its flange: `turns` bands, each the front half of an ellipse 0.56 as tall
    as the post is wide (the building camera), textured from the rope itself and darkened toward the post's sides."""
    a = np.array(sprite).astype(np.float32)
    al = a[:, :, 3] > 40
    h, w = al.shape
    widths = al.sum(1)
    flange = widths.max()
    rows = np.where(al.any(1))[0]
    mid = int(rows.min() + 0.6 * (rows.max() - rows.min()))
    body = int(widths[mid])
    top_flange = next(y for y in range(mid, h) if widths[y] > body + 0.25 * (flange - body))
    cols = np.where(al[mid])[0]
    cx = (cols.min() + cols.max()) / 2.0
    ra = body / 2.0 + 1.0
    rb = 0.28 * body
    st = strip.astype(np.float32)
    sh, sw = st.shape[:2]
    for t in range(turns):
        yc0 = top_flange - band * (t + 0.5) - rb * 0.5
        for x in range(int(np.floor(cx - ra)), int(np.ceil(cx + ra)) + 1):
            u = (x - cx) / ra
            if abs(u) >= 1:
                continue
            yc = yc0 + rb * np.sqrt(1 - u * u)
            shade = 0.55 + 0.45 * np.sqrt(1 - u * u)
            for y in range(int(np.floor(yc - band / 2.0)), int(np.ceil(yc + band / 2.0)) + 1):
                v = (y - (yc - band / 2.0)) / band
                if v < 0 or v > 1 or not (0 <= y < h and 0 <= x < w):
                    continue
                sx = int((x - cx + ra) * 1.7 + t * 11) % sw
                sy = min(sh - 1, int(v * sh))
                px = st[sy, sx]
                if px[3] < 40:
                    continue
                a[y, x, :3] = px[:3] * shade
                a[y, x, 3] = 255
    # where the rope leaves the wrap: the lowest band's centre at the post's side (east) and at its front (south)
    low = top_flange - band * 0.5 - rb * 0.5
    info = {"side": (cx + ra - 1, low), "front": (cx, low + rb), "band": band}
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)), info


def turn(a, facing):
    if facing == "north":
        return np.rot90(a, -1)
    if facing == "south":
        return np.rot90(a, 1)
    return a


def unturn(a, facing):
    if facing == "north":
        return np.rot90(a, 1)
    if facing == "south":
        return np.rot90(a, -1)
    return a


def ground_xy(facing, along, lateral):
    """Screen pixel of a rope-frame point (the frame measure_cable_art.py measures in)."""
    if facing == "east":
        return along * N, N / 2.0 - lateral * N
    if facing == "north":
        return N / 2.0 - lateral * N, N * (1 - along)
    return N / 2.0 + lateral * N, along * N


def ropes_only(old, ropes):
    """Rope frame: the old picture's rope pixels from just past the old attachment to the painted end, tiled back to the
    bollard's foot; everything else (the old flat fixture) dropped."""
    new = np.zeros_like(old)
    for r in ropes:
        c = N / 2.0 - r["lateral"] * N - 0.5
        half = r["thick"] * N / 2.0 + 2
        r0, r1 = int(np.floor(c - half)), int(np.ceil(c + half)) + 1
        start = int(np.ceil(r["attach"] * N)) + 4
        end = int(round(r["end"] * N))
        new[r0:r1, start:end] = old[r0:r1, start:end]
        period = 24
        for x in range(int(BASE_ALONG * N), start):
            src = x + period * int(np.ceil((start - x) / float(period)))
            new[r0:r1, x] = old[r0:r1, src]
    return new


def strand(canvas, p0, p1, width, strip):
    """A straight piece of rope from p0 to p1 (canvas px), textured along its length from the rope strip."""
    a = np.array(canvas).astype(np.float32)
    st = strip.astype(np.float32)
    sh, sw = st.shape[:2]
    (x0, y0), (x1, y1) = p0, p1
    d = np.hypot(x1 - x0, y1 - y0)
    if d < 1:
        return canvas
    ux, uy = (x1 - x0) / d, (y1 - y0) / d
    for y in range(int(min(y0, y1) - width), int(max(y0, y1) + width) + 1):
        for x in range(int(min(x0, x1) - width), int(max(x0, x1) + width) + 1):
            t = (x - x0) * ux + (y - y0) * uy
            n = -(x - x0) * uy + (y - y0) * ux
            if t < 0 or t > d or abs(n) > width / 2.0 or not (0 <= x < a.shape[1] and 0 <= y < a.shape[0]):
                continue
            px = st[min(sh - 1, int((n / width + 0.5) * sh)), int(t * 1.5) % sw]
            if px[3] < 40:
                continue
            a[y, x, :3] = px[:3]
            a[y, x, 3] = 255
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def paste(canvas, sprite, gx, gy):
    """Paste a bollard so its foot (the flange ellipse's centre) sits on ground pixel (gx, gy)."""
    w, h = sprite.size
    foot_y = h - FLANGE_HALF * w
    x, y = int(round(gx - w / 2.0)), int(round(gy - foot_y))
    canvas.alpha_composite(sprite, (x, y))
    return x, y


def main():
    root = TEX
    if "--out" in sys.argv:
        root = sys.argv[sys.argv.index("--out") + 1]
    table = json.load(open(OLD))["anchors"]
    bs = bollards()
    sb_in = os.path.join(TEX, "RimMandrake", "FlowWorks", "SuspensionBridge")
    sb_out = os.path.join(root, "RimMandrake", "FlowWorks", "SuspensionBridge")
    n = 0
    for look in LOOKS:
        for mat in MATS:
            for f in ("east", "north", "south"):   # east first: its rope strip textures the wrap
                name = "RM_SuspensionAnchor_%s_%s.png" % (mat, f)
                old = np.array(Image.open(os.path.join(sb_in, look, name)).convert("RGBA"))
                ropes = table["%s/%s/%s" % (look, mat, f)]
                canvas = Image.fromarray(np.ascontiguousarray(unturn(ropes_only(turn(old, f), ropes), f)))
                if f == "east":
                    strip = rope_strip(old, ropes[0])
                post, info = wrap(bs[(look, mat)], strip)
                # paint the bollard farther from the camera (smaller screen y) first
                feet = sorted((ground_xy(f, BASE_ALONG, r["lateral"]) for r in ropes), key=lambda p: p[1])
                for gx, gy in feet:
                    ox, oy = paste(canvas, post, gx, gy)
                    # the rope leaves the wrap and runs down to the ground toward the deck (art-eval r2 DESC_MISS: "no
                    # connecting strand between the wrap and the outgoing rope"); north: behind the post, unseen
                    w = post.size[0]
                    if f == "east":
                        sx, sy = info["side"]
                        canvas = strand(canvas, (ox + sx, oy + sy), (gx + w / 2.0 + 2, gy), info["band"] + 1, strip)
                    elif f == "south":
                        sx, sy = info["front"]
                        canvas = strand(canvas, (ox + sx, oy + sy), (gx, gy + FLANGE_HALF * w + 3), info["band"] + 1, strip)
                os.makedirs(os.path.join(sb_out, look), exist_ok=True)
                canvas.save(os.path.join(sb_out, look, name))
                n += 1
    print("wrote %d pictures under %s" % (n, sb_out))


if __name__ == "__main__":
    main()
