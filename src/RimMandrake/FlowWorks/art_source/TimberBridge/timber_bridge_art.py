#!/usr/bin/env python3
"""RIMMANDRAKE_REDRAW_TIMBER_BRIDGE_FROM_HIS_THREE_PHOTOS: the timber ("plank") suspension bridge as his walk of 2026-11-25
asked: "For the Timber bridge, it's just all wrong. Here are the right looks to emulate: [his photos 13, 14, 15] No ropes
tied to the ground for the wood bridge." (D:\\ClaudeWork\\rimmandrake\\showings\\FLOWWORKS_WALK3_20261125\\13.png, 14.png,
15.png.)

What the three photos share, and what this draws: a beam bridge. Two heavy timber stringers carry dense cross planks laid
edge to edge with thin gaps (photos 13, 15); a heavy timber curb rail runs along each side on top of the planks, bolted
through (photo 13); each end rests on a heavy timber sill on the bank (photo 13); no towers, no cables, no ropes, no
bollards. Posts with a top rail and knee braces (photo 14) are drawn by the game (RM_DeckArt, with their sun shadows) only
on a square whose Railings switch is on.

Painted procedurally (no image service), with no directional light in the paint: the pieces are turned to the bridge's
run in game, so every shadow that has a direction is computed by the game. Each of the four looks keeps its own set's
palette and accents (sampled from that look's old deck atlas); "base" is the unstyled deck.

    timber_bridge_art.py make      write the parts to out/<look>/ (beside this file)
    timber_bridge_art.py check     the geometry checks (exit 1 on a fault)
    timber_bridge_art.py preview   a mock bridge on a dug hole per look, for the eye and the judge (out/preview_*.png)

Parts (texPaths under Textures/, <dir> = Things/Building/FlowWorks/SuspensionBridge for base,
RimMandrake/FlowWorks/SuspensionBridge/<Look> for a look):
  <dir>/RM_SuspensionDeck_Timber_Strip_{root,mid,tip,solo}[_top|_bottom|_open]   the deck, drawn running east
  <dir>/RM_SuspensionDeck_Timber_Abutment[_top|_bottom|_open]                    an end on the bank, deck to the east
  RimMandrake/FlowWorks/SuspensionBridge/Cables/RM_Rail_Timber[_<Look>]          the rail beam, runs left to right
The lane suffix: a bridge 2+ squares wide draws "_top" on the lane left of its run (only that side's curb and stringer),
"_bottom" on the right-most lane, "_open" between (RM_DeckArtMath.LaneEdge); a 1-wide bridge draws no suffix.
"""
from __future__ import annotations

import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FW = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "out")
T = 256                        # px per cell
SEED = 20261126

# geometry (px across a 256 px cell, y down from the picture's top = left of the run); the C# extension carries the
# rail line (deckWidth = 2 x CURB_LAT) and the selftest keeps the two equal
PLANKS = 9                     # cross planks per cell; a gap sits on every piece edge, so no plank crosses a seam
GAP = 3.0                      # px between planks
PLANK_END = 18                 # planks run from y = PLANK_END to T - PLANK_END (1-wide)
STRINGER = (10, 22)            # the stringer's visible outer edge, under the plank ends
CURB = (26, 52)                # the curb rail on the planks
CURB_LAT = (T / 2 - (CURB[0] + CURB[1]) / 2) / T      # 0.3477 cells: the curb's centre line, where railing posts stand
SILL_X = (70, 114)             # the abutment's sill (x, deck to the east)
SILL_Y = (2, 254)              # the sill's length across (1-wide)
DECK_START = T - 6 * T / PLANKS   # the abutment's first plank edge (x): whole planks to its east edge, a gap on the seam
RAIL_PX = (256, 32)            # the rail texture, runs left to right

LOOKS = {
    # plank base rgb, plank tone spread, curb rgb, stringer rgb, sill rgb, metal rgb (bolts/straps), accent
    "base": dict(plank=(128, 100, 72), spread=0.06, curb=(142, 112, 80), stringer=(78, 60, 44), sill=(116, 90, 64),
                 metal=(70, 72, 76), accent=None),
    "Scrapper": dict(plank=(120, 84, 56), spread=0.10, curb=(132, 92, 60), stringer=(72, 52, 36), sill=(106, 76, 52),
                     metal=(122, 74, 46), accent="scrap"),
    "Industrial": dict(plank=(104, 76, 54), spread=0.08, curb=(96, 72, 52), stringer=(54, 46, 36), sill=(86, 66, 48),
                       metal=(62, 64, 68), accent="hazard"),
    "Modern": dict(plank=(204, 160, 110), spread=0.05, curb=(194, 150, 102), stringer=(112, 104, 100), sill=(170, 132, 92),
                   metal=(150, 154, 160), accent="steel"),
    "Futuristic": dict(plank=(184, 122, 62), spread=0.05, curb=(176, 118, 64), stringer=(150, 154, 162), sill=(160, 108, 58),
                       metal=(200, 206, 214), accent="glow"),
}
LANES = ("", "_top", "_bottom", "_open")
PIECES = ("root", "mid", "tip", "solo")


def stable(word):
    """A seed from a word that is the same in every process (str hash is salted per run)."""
    return sum((i + 1) * ord(c) for i, c in enumerate(word))


def tex_dir(look):
    return "Things/Building/FlowWorks/SuspensionBridge" if look == "base" else "RimMandrake/FlowWorks/SuspensionBridge/" + look


def rail_name(look):
    return "RimMandrake/FlowWorks/SuspensionBridge/Cables/RM_Rail_Timber" + ("" if look == "base" else "_" + look)


def smooth_noise(rng, h, w, cell):
    """Value noise: a coarse random grid blown up with bilinear smoothing, in [-1, 1]."""
    gh, gw = h // cell + 2, w // cell + 2
    g = rng.uniform(-1, 1, (gh, gw)).astype(np.float32)
    im = Image.fromarray(((g + 1) * 127.5).astype(np.uint8)).resize((gw * cell, gh * cell), Image.BICUBIC)
    return (np.asarray(im, dtype=np.float32)[:h, :w] / 127.5) - 1


def grain(rng, h, w, along_x):
    """Wood grain: fine streaks along the board's length, with a slow wobble."""
    if along_x:
        rows = rng.normal(0, 1, h).astype(np.float32)
        rows = np.convolve(rows, np.ones(2) / 2, mode="same")
        wob = smooth_noise(rng, h, w, 32) * 1.5
        yy = (np.arange(h)[:, None] + wob).clip(0, h - 1)
        g = np.interp(yy.ravel(), np.arange(h), rows).reshape(h, w)
    else:
        return grain(rng, w, h, True).T
    return g


def periodic_grain(look, what, h, w):
    """Grain along x that repeats every cell (T px) and is the same in every piece of a look: a curb, stringer or sill
    runs on across a piece seam without a jump."""
    r = np.random.default_rng((SEED, stable(look), stable(what), h))
    rows = np.convolve(r.normal(0, 1, h + 8), np.ones(2) / 2, mode="same")[:h]
    ph = r.uniform(0, 2 * np.pi, 3)
    x = np.arange(w, dtype=np.float32)
    wob = 1.4 * np.sin(2 * np.pi * x / T + ph[0]) + 0.7 * np.sin(4 * np.pi * x / T + ph[1])
    y = np.arange(h, dtype=np.float32)[:, None]
    yy = (y + wob[None, :] * (1 + 0.5 * np.sin(y / 9 + ph[2]))).clip(0, h - 1)
    return np.interp(yy.ravel(), np.arange(h), rows).reshape(h, w).astype(np.float32)


def blank(h, w):
    return np.zeros((h, w, 4), np.float32)


def paint(dst, mask, rgb, alpha=255.0):
    """Paint rgb (h,w,3 or a tuple) where mask (0..1) is set, alpha-over."""
    m = mask[..., None].astype(np.float32)
    rgb = np.broadcast_to(np.asarray(rgb, np.float32), dst[..., :3].shape)
    a0 = dst[..., 3:4] / 255.0
    a1 = m * (alpha / 255.0)
    oa = a1 + a0 * (1 - a1)
    dst[..., :3] = np.where(oa > 0, (rgb * a1 + dst[..., :3] * a0 * (1 - a1)) / np.maximum(oa, 1e-6), dst[..., :3])
    dst[..., 3:4] = oa * 255


def darken(dst, amount):
    """Multiply rgb by (1 - amount) where amount (h,w) is set (shading without changing alpha)."""
    dst[..., :3] *= (1 - np.clip(amount, 0, 1))[..., None]


def box(h, w, x0, x1, y0, y1, soft=0.0):
    """A rectangle mask [x0,x1) x [y0,y1) with optional soft edges (px)."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    if soft <= 0:
        return ((xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)).astype(np.float32)
    dx = np.minimum(xx - x0, x1 - xx)
    dy = np.minimum(yy - y0, y1 - yy)
    return np.clip(np.minimum(dx, dy) / soft + 0.5, 0, 1)


def dot(h, w, cx, cy, r):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    d = np.hypot(xx - cx, yy - cy)
    return np.clip(r + 0.5 - d, 0, 1)


def bolt(dst, cx, cy, r, metal, rust=False):
    h, w = dst.shape[:2]
    m = np.asarray(metal, np.float32)
    paint(dst, dot(h, w, cx + 0.6, cy + 0.6, r + 1.0), m * 0.35, 200)      # seat ring (no light direction)
    paint(dst, dot(h, w, cx, cy, r), m * (0.85 if not rust else 0.7))
    paint(dst, dot(h, w, cx - r * 0.25, cy - r * 0.25, r * 0.45), np.minimum(m * 1.35, 255), 200)


# ---------------------------------------------------------------- the deck field (pieces, lane variants)


def deck_field(look, lanes, length_px, x0_px, rng, sides=(True, True), kind="abut"):
    """A deck lanes x T tall, length_px long, whose planks start at x = x0_px. Returns rgba. sides: draw the top/bottom
    edge (stringer, plank ends, curb)."""
    L = LOOKS[look]
    H = T * lanes
    W = length_px
    a = blank(H, W)
    top_end = PLANK_END if sides[0] else -2
    bot_end = H - PLANK_END if sides[1] else H + 2
    # stringers (under the plank ends; flat, dark)
    for s, on in ((0, sides[0]), (1, sides[1])):
        if not on:
            continue
        y0, y1 = (STRINGER if s == 0 else (H - STRINGER[1], H - STRINGER[0]))
        st = box(H, W, x0_px - 2, W, y0, y1)
        col = np.asarray(L["stringer"], np.float32) * (1 + 0.10 * periodic_grain(look, "stringer", H, W)[..., None])
        paint(a, st, col)
        # the stringer's two arrises read darker (it is seen from above, below the planks)
        darken(a, 0.30 * (box(H, W, x0_px - 2, W, y0, y0 + 2) + box(H, W, x0_px - 2, W, y1 - 2, y1)))
    # planks
    pitch = T / PLANKS
    yy = np.arange(H, dtype=np.float32)[:, None]
    k0 = int(np.floor((0 - x0_px) / pitch)) - 1
    k1 = int(np.ceil((W - x0_px) / pitch)) + 1
    g = grain(rng, H, W, False)          # streaks along the plank (across the deck)
    for k in range(k0, k1):
        px0 = x0_px + k * pitch + GAP / 2
        px1 = x0_px + (k + 1) * pitch - GAP / 2
        if px1 <= max(0, x0_px) or px0 >= W:
            continue
        kr = np.random.default_rng((SEED, stable(look), stable(kind), k % PLANKS))
        tone = 1 + L["spread"] * kr.uniform(-1, 1)
        hue = kr.uniform(-0.04, 0.04)
        # ragged plank ends (each plank cut a little differently)
        e0 = top_end + kr.uniform(-2.0, 2.0)
        e1 = bot_end + kr.uniform(-2.0, 2.0)
        m = box(H, W, max(px0, x0_px), px1, e0, e1, soft=0.8)
        base = np.asarray(L["plank"], np.float32) * tone
        base = base * np.array([1 + hue, 1, 1 - hue], np.float32)
        col = base[None, None, :] * (1 + 0.09 * g[..., None]) * (1 + 0.05 * smooth_noise(kr, H, W, 24)[..., None])
        paint(a, m, col)
        # wear: the walked middle of the deck a touch lighter, plank edges a touch darker (no direction)
        mid = np.exp(-((yy - H / 2) / (H * 0.32)) ** 2)
        a[..., :3] += (m * mid * 10)[..., None] * (1 if look != "Futuristic" else 0.4)
        edge = box(H, W, px0, px0 + 1.5, e0, e1) + box(H, W, px1 - 1.5, px1, e0, e1)
        darken(a, 0.22 * edge * m)
        # end grain at a cut plank end (a thin darker band)
        if sides[0]:
            darken(a, 0.25 * box(H, W, px0, px1, e0, e0 + 2.0) * m)
        if sides[1]:
            darken(a, 0.25 * box(H, W, px0, px1, e1 - 2.0, e1) * m)
        # a knot now and then
        if kr.uniform() < 0.35:
            ky = kr.uniform(e0 + 30, e1 - 30) if e1 - e0 > 80 else (e0 + e1) / 2
            kx = (px0 + px1) / 2 + kr.uniform(-4, 4)
            darken(a, 0.35 * dot(H, W, kx, ky, kr.uniform(1.6, 2.8)) * m)
        # nails where the plank crosses each stringer (and a centre stringer on a wide deck)
        nail_ys = []
        if sides[0]:
            nail_ys.append(sum(STRINGER) / 2)
        if sides[1]:
            nail_ys.append(H - sum(STRINGER) / 2)
        if not sides[0] and not sides[1]:
            nail_ys.append(H / 2)
        for ny in nail_ys:
            for nx in ((px0 + px1) / 2 - 5, (px0 + px1) / 2 + 5):
                paint(a, dot(H, W, nx, ny, 1.3), np.asarray(L["metal"], np.float32) * 0.6, 230)
        # look accents on planks
        if L["accent"] == "scrap" and kr.uniform() < 0.18:
            # a patched plank: a rusty strap nailed across it
            sy = kr.uniform(e0 + 40, e1 - 40) if e1 - e0 > 100 else (e0 + e1) / 2
            strap = box(H, W, px0, px1, sy - 4, sy + 4)
            paint(a, strap, np.asarray(L["metal"], np.float32) * (1 + 0.15 * smooth_noise(kr, H, W, 6)[..., None]))
            for nx in (px0 + 4, px1 - 4):
                paint(a, dot(H, W, nx, sy, 1.4), (60, 40, 30))
    # the gaps between planks (no light direction: a dark slot)
    # the curbs (on top of the planks)
    for s, on in ((0, sides[0]), (1, sides[1])):
        if not on:
            continue
        y0, y1 = (CURB if s == 0 else (H - CURB[1], H - CURB[0]))
        cx0 = x0_px + 6 if x0_px > 0 else 0
        # contact shadow on the planks either side of the curb (ambient, symmetric)
        sh = np.clip(1 - np.abs(yy - (y0 + y1) / 2) / ((y1 - y0) / 2 + 7), 0, 1) * box(H, W, cx0 - 4, W, 0, H)
        darken(a, 0.35 * sh * (a[..., 3] > 0))
        cm = box(H, W, cx0, W, y0, y1, soft=0.8)
        cg = periodic_grain(look, "curb", H, W)
        col = np.asarray(L["curb"], np.float32)[None, None, :] * (1 + 0.10 * cg[..., None])
        paint(a, cm, col)
        # rounded top: a faint lighter crown, darker arrises (symmetric)
        crown = np.exp(-((yy - (y0 + y1) / 2) / ((y1 - y0) * 0.28)) ** 2)
        a[..., :3] += (cm * crown * 12)[..., None]
        darken(a, 0.28 * (box(H, W, cx0, W, y0, y0 + 2) + box(H, W, cx0, W, y1 - 2, y1)))
        # a butt joint inside some pieces (never on a piece edge, so the seam stays hidden) and through-bolts
        jx = {"root": 168, "tip": 88, "mid": 120 if s == 0 else 200}.get(kind)
        if jx is not None and cx0 + 8 < jx < W - 8:
            darken(a, 0.55 * box(H, W, jx - 1, jx + 1, y0, y1))
        for bx in range(T // 4, W, T // 2):
            if bx > cx0 + 6:
                bolt(a, bx, (y0 + y1) / 2, 3.0 if L["accent"] != "glow" else 2.4, L["metal"], rust=L["accent"] == "scrap")
        if L["accent"] == "steel":
            # a steel angle along the curb's outer arris
            oy = (y0, y0 + 4) if s == 0 else (y1 - 4, y1)
            paint(a, box(H, W, cx0, W, *oy), np.asarray(L["metal"], np.float32) * (1 + 0.05 * cg[..., None]))
            darken(a, 0.25 * box(H, W, cx0, W, oy[0] + (3 if s == 0 else 0), oy[0] + (4 if s == 0 else 1)))
        if L["accent"] == "glow":
            # a thin light line along the curb's inner face
            ly = (y1 - 4, y1 - 2) if s == 0 else (y0 + 2, y0 + 4)
            paint(a, box(H, W, cx0 + 2, W, *ly), (120, 230, 245), 230)
            paint(a, box(H, W, cx0 + 2, W, ly[0] - 1, ly[1] + 1), (120, 230, 245), 70)
        if L["accent"] == "hazard":
            # a steel cap plate along the curb top, black and yellow at each butt joint
            paint(a, box(H, W, cx0, W, y0 + 3, y1 - 3), np.asarray(L["metal"], np.float32) * (1 + 0.06 * cg[..., None]), 235)
            for jx in range(T // 2, W + T, T):
                if cx0 + 10 < jx < W - 10:
                    for q in range(-3, 3):
                        stripe = box(H, W, jx + q * 6, jx + q * 6 + 3, y0 + 3, y1 - 3)
                        paint(a, stripe, (214, 170, 40) if q % 2 == 0 else (30, 30, 30))
    return a


def piece(look, kind, lane):
    """One deck piece (T x T, running east) of a look, kind root/mid/tip/solo, lane suffix."""
    if lane == "":
        return deck_field(look, 1, T, 0, np.random.default_rng((SEED, stable(look), stable(kind), 1)), kind=kind)
    # every lane variant of one piece is cut from one 3-lane field, so planks and grain run on across the lane seam
    f = deck_field(look, 3, T, 0, np.random.default_rng((SEED, stable(look), stable(kind), 3)), kind=kind)
    i = {"_top": 0, "_open": 1, "_bottom": 2}[lane]
    return f[i * T:(i + 1) * T].copy()


def abutment(look, lane):
    """An end on the bank (T x T, the deck to the east): the deck's last planks and curbs resting on a heavy sill."""
    L = LOOKS[look]
    rng = np.random.default_rng((SEED, 99, stable(look), 1 if lane == "" else 3))
    lanes, i = (1, 0) if lane == "" else (3, {"_top": 0, "_open": 1, "_bottom": 2}[lane])
    H = T * lanes
    a = blank(H, T)
    # the sill: a heavy timber across, longer than the deck is wide; on a wide bridge one sill runs under every lane
    sy0 = SILL_Y[0]
    sy1 = H - (T - SILL_Y[1])
    yy, xx = np.mgrid[0:H, 0:T].astype(np.float32) + 0.5
    # ground contact shadow round the sill (symmetric, soft)
    d = np.maximum(np.maximum(SILL_X[0] - xx, xx - SILL_X[1]), np.maximum(sy0 - yy, yy - sy1))
    paint(a, np.clip(1 - d / 7.0, 0, 1) * (d > 0), (20, 16, 12), 110)
    sm = box(H, T, *SILL_X, sy0, sy1, soft=0.8)
    sg = grain(rng, H, T, False)
    paint(a, sm, np.asarray(L["sill"], np.float32)[None, None, :] * (1 + 0.10 * sg[..., None])
          * (1 + 0.06 * smooth_noise(rng, H, T, 32)[..., None]))
    darken(a, 0.30 * (box(H, T, SILL_X[0], SILL_X[0] + 2, sy0, sy1) + box(H, T, SILL_X[1] - 2, SILL_X[1], sy0, sy1)))
    # end grain at the sill's two ends (rings)
    for ey, s in ((sy0, 1), (sy1, -1)):
        eg = box(H, T, *SILL_X, min(ey, ey + 6 * s), max(ey, ey + 6 * s))
        paint(a, eg, np.asarray(L["sill"], np.float32) * 0.78)
        cx = (SILL_X[0] + SILL_X[1]) / 2
        rings = np.sin(np.hypot(xx - cx, (yy - ey) * 3) * 0.9) * 0.08
        darken(a, (rings + 0.08) * eg)
    if L["accent"] == "hazard":
        for ey in (sy0 + 8, sy1 - 22):
            for q in range(4):
                paint(a, box(H, T, *SILL_X, ey + q * 4 - 1 + 0.0, ey + q * 4 + 1.5), (214, 170, 40) if q % 2 == 0 else (30, 30, 30))
    if L["accent"] == "steel":
        for ey in (sy0 + 10, sy1 - 10):
            paint(a, box(H, T, SILL_X[0] - 2, SILL_X[1] + 2, ey - 3, ey + 3), np.asarray(L["metal"], np.float32))
            bolt(a, (SILL_X[0] + SILL_X[1]) / 2, ey, 2.2, L["metal"])
    # the deck, from DECK_START east, resting on the sill
    sides = (i == 0, i == lanes - 1)
    deck = deck_field(look, lanes, T, DECK_START, rng, sides=(sides[0] or lane == "", sides[1] or lane == ""))
    # the deck's shadow on the sill just west of its first plank (symmetric ambient, no direction)
    shade = np.clip(1 - (DECK_START - xx) / 6.0, 0, 1) * (xx < DECK_START) * (a[..., 3] > 0)
    darken(a, 0.35 * shade * box(H, T, 0, T, PLANK_END, H - PLANK_END))
    m = deck[..., 3] / 255.0
    a[..., :3] = deck[..., :3] * m[..., None] + a[..., :3] * (1 - m[..., None]) * (a[..., 3:4] / 255.0 > 0)
    a[..., 3] = np.maximum(a[..., 3], deck[..., 3])
    # each curb ends in a squared end-grain block, through-bolted to the sill
    for s, on in ((0, sides[0] or lane == ""), (1, sides[1] or lane == "")):
        if not on:
            continue
        y0, y1 = (CURB if s == 0 else (H - CURB[1], H - CURB[0]))
        endb = box(H, T, DECK_START + 6, DECK_START + 11, y0, y1)
        paint(a, endb, np.asarray(L["curb"], np.float32) * 0.72)
        bolt(a, (SILL_X[0] + SILL_X[1]) / 2 + 6, (y0 + y1) / 2, 3.2, L["metal"], rust=L["accent"] == "scrap")
    if lanes > 1:
        a = a[i * T:(i + 1) * T].copy()
    return a


def rail(look):
    """The rail and post beam (runs left to right), RAIL_PX: a squared timber seen from above, grain along it."""
    L = LOOKS[look]
    w, h = RAIL_PX
    rng = np.random.default_rng((SEED, 7, stable(look)))
    a = blank(h, w)
    yy = np.arange(h, dtype=np.float32)[:, None]
    g = grain(rng, h, w, True)
    col = np.asarray(L["curb"], np.float32)[None, None, :] * (1 + 0.12 * g[..., None])
    paint(a, box(h, w, 0, w, 2, h - 2, soft=0.8), col)
    crown = np.exp(-((yy - h / 2) / (h * 0.25)) ** 2)
    a[..., :3] += (crown * 14 * (a[..., 3] > 0))[..., None]
    darken(a, 0.35 * (box(h, w, 0, w, 2, 5) + box(h, w, 0, w, h - 5, h - 2)))
    if L["accent"] == "steel":
        paint(a, box(h, w, 0, w, 2, 7), np.asarray(L["metal"], np.float32))
    if L["accent"] == "glow":
        paint(a, box(h, w, 0, w, h / 2 - 1.5, h / 2 + 1.5), (120, 230, 245), 230)
    if L["accent"] == "hazard":
        paint(a, box(h, w, 0, w, 3, h - 3), np.asarray(L["metal"], np.float32) * (1 + 0.06 * g[..., None]), 220)
    return a


def save(a, rel):
    p = os.path.join(OUT, rel + ".png")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8), "RGBA").save(p)
    return p


def make():
    n = 0
    for look in LOOKS:
        d = tex_dir(look)
        for kind in PIECES:
            for lane in LANES:
                save(piece(look, kind, lane), "%s/RM_SuspensionDeck_Timber_Strip_%s%s" % (d, kind, lane))
                n += 1
        for lane in LANES:
            save(abutment(look, lane), "%s/RM_SuspensionDeck_Timber_Abutment%s" % (d, lane))
            n += 1
        save(rail(look), rail_name(look))
        n += 1
    print("made %d pictures under %s" % (n, OUT))


def load(rel, root=None):
    p = os.path.join(root or OUT, rel + ".png")
    if not os.path.exists(p):
        raise FileNotFoundError(rel)
    return np.asarray(Image.open(p).convert("RGBA"), dtype=np.float32)


def check(root=None, plant=None):
    """Geometry faults: a seam between pieces or lanes, a hole in the deck, an edge where none belongs. root: where the
    pictures are (default out/; the selftest passes the installed Textures/). plant: a fault planted in memory."""
    fails, read = [], 0
    try:
        return _check(root, plant)
    except FileNotFoundError as e:
        return ["picture not found: %s" % e], read


def _check(root, plant):
    fails, read = [], 0

    def ld(rel):
        return load(rel, root)
    for look in LOOKS:
        d = tex_dir(look)
        P = {(k, l): ld("%s/RM_SuspensionDeck_Timber_Strip_%s%s" % (d, k, l)) for k in PIECES for l in LANES}
        A = {l: ld("%s/RM_SuspensionDeck_Timber_Abutment%s" % (d, l)) for l in LANES}
        read += len(P) + len(A)
        if plant == "rope" and look == "base":
            A[""][T // 2 - 4:T // 2 + 4, 0:SILL_X[0]] = (150, 120, 80, 255)      # a ground rope to the west
        if plant == "sparse" and look == "base":
            P[("mid", "")][:, ::3, 3] = 0                                         # slats with wide gaps
        for (k, l), p in P.items():
            al = p[..., 3] > 128
            ys = np.where(al.any(1))[0]
            # the walkway is solid: no column has a gap wider than a plank gap in the middle rows
            band = al[T // 2 - 40:T // 2 + 40]
            if (~band).all(0).sum() > PLANKS * (GAP + 1.5) + 2:
                fails.append("%s %s%s: the walkway has %d open columns (planks laid edge to edge leave <= %d)"
                             % (look, k, l, (~band).all(0).sum(), PLANKS * (GAP + 1.5) + 2))
            top_open = l in ("_bottom", "_open")
            bot_open = l in ("_top", "_open")
            if top_open != bool(al[0].any()):
                fails.append("%s %s%s: top row %s" % (look, k, l, "has no deck (lane seam open)" if top_open else "is painted (no edge)"))
            if bot_open != bool(al[-1].any()):
                fails.append("%s %s%s: bottom row %s" % (look, k, l, "has no deck" if bot_open else "is painted"))
        # seams along the run: the curb and stringer rows match across every piece pair (a piece's east column vs the
        # next piece's west column)
        for l in LANES:
            for k1 in ("root", "mid"):
                for k2 in ("mid", "tip"):
                    e = P[(k1, l)][:, -1]
                    w = P[(k2, l)][:, 0]
                    diff = np.abs(e[:, 3] - w[:, 3])
                    if (diff > 128).sum() > 6:
                        fails.append("%s %s|%s%s: %d rows open on one side of the seam only" % (look, k1, k2, l, (diff > 128).sum()))
                    on = (e[:, 3] > 200) & (w[:, 3] > 200)
                    if on.any():
                        dc = np.abs(e[on, :3] - w[on, :3]).mean(1)
                        if np.percentile(dc, 90) > 40:
                            fails.append("%s %s|%s%s: colour jumps %.0f at the seam" % (look, k1, k2, l, np.percentile(dc, 90)))
        # the lanes join: _top's bottom row continues into _bottom's top row (and _open both ways)
        for up, dn in (("_top", "_bottom"), ("_top", "_open"), ("_open", "_bottom")):
            u = P[("mid", up)][-1, :, 3] > 128
            v = P[("mid", dn)][0, :, 3] > 128
            if (u != v).sum() > 4:
                fails.append("%s lanes %s|%s: plank gaps do not line up (%d columns)" % (look, up, dn, (u != v).sum()))
        # the abutment meets the deck: its east column matches a root piece's west column in coverage
        for l in LANES:
            e = A[l][:, -1, 3] > 128
            w = P[("root", l)][:, 0, 3] > 128
            if (e != w).sum() > 6:
                fails.append("%s abutment%s: east edge does not meet the deck (%d rows)" % (look, l, (e != w).sum()))
            if (A[l][:, :SILL_X[0] - 8, 3] > 200).any():
                fails.append("%s abutment%s: paint west of the sill (a rope or bollard?)" % (look, l))
        r = ld(rail_name(look))
        read += 1
        if r.shape[:2] != (RAIL_PX[1], RAIL_PX[0]):
            fails.append("%s rail: size %s" % (look, r.shape[:2]))
    return fails, read


def preview():
    """A mock 1-wide bridge (E-W, 5 deck squares) and a 2-wide one (N-S) over a dug hole, per look, at 64 px a cell."""
    s = 64
    for look in LOOKS:
        d = tex_dir(look)
        W, H = 12, 12
        bg = np.zeros((H * s, W * s, 4), np.float32)
        bg[...] = (118, 104, 78, 255)
        hole = box(H * s, W * s, 2 * s, 9 * s, 1 * s, 11 * s)
        paint(bg, hole, (46, 40, 34))

        def put(rel, cx, cy, ang):
            im = Image.open(os.path.join(OUT, rel + ".png")).convert("RGBA").resize((s, s), Image.LANCZOS).rotate(-ang)
            arr = np.asarray(im, np.float32)
            m = arr[..., 3:4] / 255.0
            sl = bg[cy * s:(cy + 1) * s, cx * s:(cx + 1) * s]
            sl[..., :3] = arr[..., :3] * m + sl[..., :3] * (1 - m)
        # E-W 1 wide, row 3: anchor at x=1, deck 2..8, anchor at 9
        put(d + "/RM_SuspensionDeck_Timber_Abutment", 1, 3, 0)
        for x in range(2, 9):
            k = "root" if x == 2 else "tip" if x == 8 else "mid"
            put(d + "/RM_SuspensionDeck_Timber_Strip_" + k, x, 3, 0)
        put(d + "/RM_SuspensionDeck_Timber_Abutment", 9, 3, 180)
        # E-W 2 wide, rows 6 (lane 0, left of an east run = north = top) and 7
        for row, lane in ((6, "_top"), (7, "_bottom")):
            put(d + "/RM_SuspensionDeck_Timber_Abutment" + lane, 1, row, 0)
            for x in range(2, 9):
                k = "root" if x == 2 else "tip" if x == 8 else "mid"
                put(d + "/RM_SuspensionDeck_Timber_Strip_" + k + lane, x, row, 0)
            far = "_bottom" if lane == "_top" else "_top"
            put(d + "/RM_SuspensionDeck_Timber_Abutment" + far, 9, row, 180)
        # N-S 1 wide at column 10, rows 0..11 over a strip of hole
        paint(bg, box(H * s, W * s, 10 * s, 11 * s, 1 * s, 11 * s), (46, 40, 34))
        put(d + "/RM_SuspensionDeck_Timber_Abutment", 10, 11, 270)
        for y in range(1, 11):
            put(d + "/RM_SuspensionDeck_Timber_Strip_mid", 10, y, 270)
        put(d + "/RM_SuspensionDeck_Timber_Abutment", 10, 0, 90)
        p = os.path.join(OUT, "preview_%s.png" % look)
        Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), "RGBA").save(p)
        print(p)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "make"
    if cmd == "make":
        make()
        return 0
    if cmd == "preview":
        preview()
        return 0
    if cmd == "check":
        fails, read = check()
        for f in fails:
            print("FAIL", f)
        print("timber bridge art: %s (%d faults, %d pictures read)" % ("FAIL" if fails else "PASS", len(fails), read))
        return 1 if fails else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
