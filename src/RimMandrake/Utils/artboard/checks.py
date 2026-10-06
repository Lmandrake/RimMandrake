"""Tier (a): deterministic per-crop pixel checks. No model, no judgement, milliseconds per crop.

Every check names WHAT it measured so a flag can be argued with. A crop is split into
  core  = the subject's own cells (+ an allowed overhang, for sprites drawn past their footprint)
  ring  = the pad around it, which should be plain ground.
Foreground = pixels that differ from the ground. With a clean plate (the same frame shot before the
subjects were staged) that is a per-pixel diff and is exact; without one it is distance from the ring's
median colour, which is good on flat ground and degrades on busy ground (say so in the report).
"""
import colorsys

import numpy as np
from PIL import Image, ImageDraw

FAMILIES = ("red", "orange", "brown", "yellow", "green", "cyan", "blue", "purple", "magenta",
            "black", "grey", "white")

DEFAULTS = {
    "fg_threshold": 40.0,      # channel-distance from ground counted as foreground
    "empty_max_fg": 0.02,      # core foreground fraction at or below this = EMPTY
    "magenta_min": 0.15,       # share of core pixels that are pure magenta = MISSING_TEXTURE
    "overflow_min": 0.04,      # ring foreground fraction above this = OVERFLOW
    "truncate_edge": 0.8,      # a bbox side this solid on an organic sprite = TRUNCATED
    "hole_min": 0.06,          # enclosed-ground share of the filled silhouette = HOLE
    "colour_min_share": 0.2,   # expected colour family must hold this share of foreground
    "off_cell": 0.3,           # foreground centroid this many cells from the core centre = OFF_CELL
    "identical_max": 6.0,      # mean abs diff below this between must-differ crops = IDENTICAL
    "ref_max": 0.10,           # share of core pixels changed (> fg_threshold) vs approved reference = REF_DRIFT
}


def family(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    h *= 360
    if v < 0.18:
        return "black"
    if s < 0.18:
        return "white" if v > 0.85 else "grey"
    if h < 15 or h >= 345:
        return "red"
    if h < 45:
        return "brown" if v < 0.55 else "orange"
    if h < 70:
        return "yellow"
    if h < 165:
        return "green"
    if h < 195:
        return "cyan"
    if h < 255:
        return "blue"
    if h < 290:
        return "purple"
    return "magenta"


def family_histogram(pixels):
    """pixels: (N,3) uint8. Quantise to 16 levels first so this stays fast on big crops."""
    if len(pixels) == 0:
        return {}
    q = (pixels // 16).astype(np.int32)
    keys, counts = np.unique(q[:, 0] * 256 + q[:, 1] * 16 + q[:, 2], return_counts=True)
    hist = {}
    for k, c in zip(keys, counts):
        r, g, b = (k // 256) * 16 + 8, ((k // 16) % 16) * 16 + 8, (k % 16) * 16 + 8
        f = family(r, g, b)
        hist[f] = hist.get(f, 0) + int(c)
    tot = float(sum(hist.values()))
    return {f: round(c / tot, 3) for f, c in sorted(hist.items(), key=lambda kv: -kv[1])}


def _fill_holes(mask):
    """Return (filled_mask, hole_mask): ground pixels not reachable from the crop border."""
    h, w = mask.shape
    im = Image.new("L", (w + 2, h + 2), 0)
    im.paste(Image.fromarray((mask * 255).astype(np.uint8)), (1, 1))
    ImageDraw.floodfill(im, (0, 0), 128)
    a = np.asarray(im)[1:-1, 1:-1]
    holes = a == 0
    return mask | holes, holes


def foreground(crop, ring_mask, plate=None, thr=40.0):
    """crop/plate: (H,W,3) arrays. Returns (fg_mask, mode, ground_rgb)."""
    c = crop.astype(np.int16)
    if plate is not None:
        d = np.abs(c - plate.astype(np.int16)).max(axis=2)
        ground = np.median(plate.reshape(-1, 3), axis=0)
        return d > thr, "plate", ground
    ring = c[ring_mask]
    ground = np.median(ring, axis=0) if len(ring) else np.median(c.reshape(-1, 3), axis=0)
    d = np.abs(c - ground).max(axis=2)
    spread = float(np.median(np.abs(d[ring_mask] - np.median(d[ring_mask])))) if ring_mask.any() else 0.0
    return d > max(thr, 4.0 * spread + 12.0), "ring", ground


def run_checks(crop, core_mask, ring_mask, subject, plate=None, ppc=32.0, cfg=None):
    """crop: (H,W,3) uint8. Returns (findings, metrics)."""
    cfg = dict(DEFAULTS, **(cfg or {}))
    exp = subject.get("expect", {})
    findings = []
    fg, mode, ground = foreground(crop, ring_mask, plate, cfg["fg_threshold"])
    core_fg = fg & core_mask
    core_n = max(1, int(core_mask.sum()))
    fg_frac = core_fg.sum() / core_n
    ring_frac = (fg & ring_mask).sum() / max(1, int(ring_mask.sum()))
    m = {"fg_mode": mode, "core_fg": round(float(fg_frac), 3), "ring_fg": round(float(ring_frac), 3),
         "ground_rgb": [int(v) for v in ground]}

    px = crop[core_mask].astype(np.int16)
    magenta = ((px[:, 0] > 200) & (px[:, 1] < 70) & (px[:, 2] > 200)).sum() / core_n
    m["magenta"] = round(float(magenta), 3)
    if magenta >= cfg["magenta_min"]:
        findings.append({"check": "MISSING_TEXTURE", "detail": "%.0f%% of the cell is pure magenta "
                         "(RimWorld's missing-texture colour)" % (100 * magenta)})

    if fg_frac <= cfg["empty_max_fg"] and not exp.get("may_be_empty"):
        hint = (" — but %.0f%% of the surrounding ring is foreground, so the subject is probably DISPLACED "
                "off its declared cell" % (100 * ring_frac)) if ring_frac > cfg["overflow_min"] else " — nothing drew here"
        findings.append({"check": "EMPTY", "detail": "only %.1f%% of the cell differs from the ground (%s mode)%s"
                         % (100 * fg_frac, mode, hint)})
        return findings, m

    ys, xs = np.nonzero(core_fg)
    cy_, cx_ = np.nonzero(core_mask)
    off = float(np.hypot(xs.mean() - cx_.mean(), ys.mean() - cy_.mean())) / ppc if len(xs) else 0.0
    m["centroid_offset_cells"] = round(off, 2)
    off_cell = off > cfg["off_cell"] and not exp.get("may_be_offset")
    if off_cell:
        findings.append({"check": "OFF_CELL", "detail": "the drawn mass sits %.2f cells from the cell centre — "
                         "subject displaced, or the board geometry is wrong" % off})

    hist = family_histogram(crop[core_fg])
    m["colours"] = dict(list(hist.items())[:4])
    want = exp.get("colour")
    if want:
        want = [want] if isinstance(want, str) else list(want)
        got = max((hist.get(f, 0) for f in want), default=0)
        if got < cfg["colour_min_share"]:
            findings.append({"check": "WRONG_COLOUR", "detail": "expected %s, foreground is %s"
                             % ("/".join(want), ", ".join("%s %.0f%%" % (k, 100 * v)
                                                          for k, v in list(hist.items())[:3]))})

    if ring_frac > cfg["overflow_min"] and not exp.get("may_overflow"):
        findings.append({"check": "OVERFLOW", "detail": "%.0f%% of the surrounding ground is covered — "
                         "the sprite draws outside its cells (or a neighbour/foreign object intrudes)"
                         % (100 * ring_frac)})

    if len(xs) and exp.get("organic", True) and not off_cell:
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        # a side lying ON the core boundary is our crop cutting the sprite, not the texture being cut
        bx0, bx1, by0, by1 = cx_.min(), cx_.max(), cy_.min(), cy_.max()
        sides = {"left": (core_fg[y0:y1 + 1, x0], x0 == bx0), "right": (core_fg[y0:y1 + 1, x1], x1 == bx1),
                 "top": (core_fg[y0, x0:x1 + 1], y0 == by0), "bottom": (core_fg[y1, x0:x1 + 1], y1 == by1)}
        solid = {k: float(v.mean()) for k, (v, at_edge) in sides.items()
                 if len(v) >= max(6, 0.25 * ppc) and not at_edge}
        cut = [k for k, v in solid.items() if v >= cfg["truncate_edge"]]
        m["edge_solidity"] = {k: round(v, 2) for k, v in solid.items()}
        if cut:
            findings.append({"check": "TRUNCATED", "detail": "a ruler-straight solid %s edge on an organic "
                             "sprite — the texture is cut off at its draw rect" % "/".join(cut)})

    if not exp.get("holes_ok"):
        filled, holes = _fill_holes(fg)
        holes &= core_mask
        hshare = holes.sum() / max(1, int((filled & core_mask).sum()))
        m["holes"] = round(float(hshare), 3)
        if hshare >= cfg["hole_min"] and holes.sum() >= 0.05 * ppc * ppc:
            why = ("an alpha hole or missing layer" if mode == "plate" else
                   "an alpha hole, a missing layer, OR a body filled with the ground's own colour — ring mode "
                   "cannot tell these apart; reshoot with a clean plate")
            findings.append({"check": "HOLE", "detail": "%.0f%% of the silhouette is enclosed ground-coloured "
                             "pixels: %s" % (100 * hshare, why)})
    return findings, m


def changed_share(a, b, thr=40.0):
    """Share of pixels whose max channel difference exceeds thr, b resized to a's size. Robust to ground
    noise in a way a mean difference is not (a mean dilutes a changed sprite by the ground around it)."""
    if a.shape != b.shape:
        b = np.asarray(Image.fromarray(b).resize((a.shape[1], a.shape[0]), Image.BILINEAR))
    return float((np.abs(a.astype(np.int16) - b.astype(np.int16)).max(axis=2) > thr).mean())


def mean_abs_diff(a, b):
    """Mean absolute channel difference of two crops, b resized to a's size."""
    if a.shape != b.shape:
        b = np.asarray(Image.fromarray(b).resize((a.shape[1], a.shape[0]), Image.BILINEAR))
    return float(np.abs(a.astype(np.int16) - b.astype(np.int16)).mean())
