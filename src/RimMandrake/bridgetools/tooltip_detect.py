#!/usr/bin/env python3
"""Find a drawn tooltip in a hovered screenshot by comparing it with an unhovered one (PIL only, no numpy).

Used by prove_hover_tooltip.py (item PLAYER_HOVER_PROBE_TOOLTIP_DRAWN). A RimWorld tooltip is a dark filled box with
light text, drawn on top of everything near the cursor. The detector therefore asks: is there a region that CHANGED
between the two frames, whose box is mostly dark and carries a modest share of light (text) pixels? A gizmo's own
mouse-over brightening changes pixels too, but it is bright, not a dark box with text, so it does not pass.

Separately it reports whether the bottom-left mouse-over readout (the map's "what is under the cursor" text, which is
not a tooltip box) changed: that is how vanilla answers a hover on a map thing.
"""
from collections import deque

from PIL import Image, ImageChops

CELL = 4            # mask is reduced to CELL x CELL blocks before the component search
DIFF_MIN = 40       # a channel change below this is noise (JPEG-free PNGs; animation is paused)
MIN_W, MIN_H = 40, 16
MAX_FRAC = 0.6      # a "box" wider or taller than this share of the frame is a scene change, not a tooltip
DARK_L, TEXT_L = 75, 165
DARK_SHARE = 0.45
TEXT_MIN, TEXT_MAX_SHARE = 25, 0.40


def _changed_mask(a, b):
    """Block mask (list of rows of bool) where any pixel in the block changed by >= DIFF_MIN on some channel."""
    d = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    r, g, bl = d.split()
    m = ImageChops.lighter(ImageChops.lighter(r, g), bl).point(lambda v: 255 if v >= DIFF_MIN else 0)
    w, h = m.size
    bw, bh = (w + CELL - 1) // CELL, (h + CELL - 1) // CELL
    small = m.resize((bw, bh), Image.BOX)   # any changed pixel makes the block > 0
    px = small.load()
    return [[px[x, y] > 0 for x in range(bw)] for y in range(bh)], bw, bh


def _components(mask, bw, bh):
    """Bounding boxes (x0,y0,x1,y1 in block units, inclusive) of 8-connected changed regions, gap-bridged by 1 block."""
    seen = [[False] * bw for _ in range(bh)]
    out = []
    for y in range(bh):
        for x in range(bw):
            if not mask[y][x] or seen[y][x]:
                continue
            q = deque([(x, y)])
            seen[y][x] = True
            x0 = x1 = x
            y0 = y1 = y
            while q:
                cx, cy = q.popleft()
                x0, x1, y0, y1 = min(x0, cx), max(x1, cx), min(y0, cy), max(y1, cy)
                for dy in (-2, -1, 0, 1, 2):
                    for dx in (-2, -1, 0, 1, 2):
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < bw and 0 <= ny < bh and mask[ny][nx] and not seen[ny][nx]:
                            seen[ny][nx] = True
                            q.append((nx, ny))
            out.append((x0, y0, x1, y1))
    return out


def _shares(img, box):
    """(dark share, text pixel count, text share) of the luminance crop `box` (full-res x0,y0,x1,y1 exclusive)."""
    crop = img.convert("L").crop(box)
    hist = crop.histogram()
    n = sum(hist) or 1
    dark = sum(hist[:DARK_L])
    text = sum(hist[TEXT_L:])
    return dark / n, text, text / n


def find_tooltip(base, hover):
    """{'drawn': bool, 'box': [x0,y0,x1,y1] or None, 'candidates': [...]} for two same-size PIL images."""
    if base.size != hover.size:
        return {"drawn": False, "box": None, "candidates": [], "error": "size mismatch %s vs %s" % (base.size, hover.size)}
    w, h = hover.size
    mask, bw, bh = _changed_mask(base, hover)
    cands = []
    for (x0, y0, x1, y1) in _components(mask, bw, bh):
        box = (x0 * CELL, y0 * CELL, min(w, (x1 + 1) * CELL), min(h, (y1 + 1) * CELL))
        bwid, bhei = box[2] - box[0], box[3] - box[1]
        if bwid < MIN_W or bhei < MIN_H or bwid > MAX_FRAC * w or bhei > MAX_FRAC * h:
            continue
        dark, text, tshare = _shares(hover, box)
        ok = dark >= DARK_SHARE and text >= TEXT_MIN and tshare <= TEXT_MAX_SHARE
        cands.append({"box": list(box), "dark": round(dark, 3), "textPx": text, "textShare": round(tshare, 3), "tooltip": ok})
    cands.sort(key=lambda c: (not c["tooltip"], -(c["box"][2] - c["box"][0]) * (c["box"][3] - c["box"][1])))
    best = next((c for c in cands if c["tooltip"]), None)
    return {"drawn": best is not None, "box": best["box"] if best else None, "candidates": cands[:8]}


def readout_changed(base, hover):
    """Did light text change in the bottom-left mouse-over readout zone (x < 30% W, y > 70% H)?"""
    w, h = hover.size
    box = (0, int(0.7 * h), int(0.3 * w), h)
    a, b = base.convert("L").crop(box), hover.convert("L").crop(box)
    d = ImageChops.difference(a, b).point(lambda v: 255 if v >= DIFF_MIN else 0)
    changed = d.histogram()[255]
    _, text, _ = _shares(hover, box)
    return {"changed": changed >= TEXT_MIN, "changedPx": changed, "textPx": text, "box": list(box)}
