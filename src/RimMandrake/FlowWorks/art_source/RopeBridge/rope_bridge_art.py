#!/usr/bin/env python3
"""RIMMANDRAKE_REDRAW_ROPE_BRIDGE_AS_ROPES_AND_SPARSE_SLATS: the rope suspension bridge as his walk of 2026-11-25 asked
(stations 48/49/70, reference photo FLOWWORKS_WALK3_20261125/12.png): "Ropes along the sides with planks laid upon the
ropes ... sparse wood slats on a rope bridge, that's it"; hand-guide ropes always; rope netting when railings are on; the
ground ropes in line with the bridge's sides.

Derived, no image service: every part is cut from the rope bridge's own painted pictures (its old deck planks, its bollard
anchors) or recoloured from the picked cable set, so the palette and brushwork stay the set's.

    rope_bridge_art.py make      write the parts to out/ (beside this file)
    rope_bridge_art.py check     the geometry checks (exit 1 on a fault)

Parts (texPaths under Textures/):
  Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionDeck_Rope_Strip_{root,mid,tip,solo}  the deck, drawn running east
  Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionDeck_Rope_Post                       a hand-rope post (foot at bottom)
  RimMandrake/FlowWorks/SuspensionBridge/Cables/RM_Cable_Rope                                  hemp rope, runs left to right
  Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionAnchor_Rope_{east,north,south}       bollards moved out to the sides
  Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionDeck_Rope                            the menu icon (runs north)
Inputs are read from git (the pictures as they were at BASE), so a re-run after install makes the same bytes.
"""
from __future__ import annotations

import io
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FW = os.path.normpath(os.path.join(HERE, "..", ".."))
REPO = os.path.normpath(os.path.join(FW, "..", "..", ".."))
OUT = os.path.join(HERE, "out")
SB = "Things/Building/FlowWorks/SuspensionBridge"
TEXREL = "src/RimMandrake/FlowWorks/Textures"
BASE = "eea38566a8"            # the commit whose rope pictures are the sources (before this redraw installed anything)
T = 256                        # px per cell
SEED = 20261125

# geometry (cells); the C# extension on RM_SuspensionDeck_Rope carries the same numbers (selftest_flowworks_rope_bridge.py)
ANCHOR_SHIFT = 44              # px each bollard half moves out from the centre line (the most the east view's top bollard allows)
SLATS = 3                      # slats per cell, centred at (k + 0.5) / SLATS: none crosses a piece edge
SLAT_W = 26                    # px along the run
SLAT_HALF = 0.39               # slat half-length across the deck
ROPE_THICK = 10                # px, the anchors' painted rope (measured 0.039 cells)


def git_png(rel):
    raw = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (BASE, rel)], capture_output=True, check=True).stdout
    return np.asarray(Image.open(io.BytesIO(raw)).convert("RGBA"), dtype=np.float32)


def save(a, name):
    os.makedirs(OUT, exist_ok=True)
    Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8), "RGBA").save(os.path.join(OUT, name + ".png"))


def resize(a, w, h):
    im = Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8), "RGBA")
    return np.asarray(im.resize((w, h), Image.LANCZOS), dtype=np.float32)


def over(dst, src, x, y):
    """Alpha-composite src onto dst with its top-left at (x, y), clipped."""
    h, w = src.shape[:2]
    H, W = dst.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x0 >= x1 or y0 >= y1:
        return
    s = src[y0 - y:y1 - y, x0 - x:x1 - x]
    d = dst[y0:y1, x0:x1]
    sa = s[..., 3:4] / 255.0
    da = d[..., 3:4] / 255.0
    oa = sa + da * (1 - sa)
    rgb = np.where(oa > 0, (s[..., :3] * sa + d[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-6), 0)
    d[..., :3] = rgb
    d[..., 3:4] = oa * 255


# ------------------------------------------------------------------------------------------------------------- rope
def rope_texture():
    """The picked black wire rope (generated/cables/black.png) recoloured to tan hemp: its own twist and shading."""
    src = np.asarray(Image.open(os.path.join(FW, "art_source", "JettyBridgeRedesign", "generated", "cables", "black.png"))
                     .convert("RGBA"), dtype=np.float32)
    lum = src[..., :3] @ np.array([0.299, 0.587, 0.114])
    on = src[..., 3] > 128
    lo, hi = np.percentile(lum[on], 3), np.percentile(lum[on], 97)
    t = np.clip((lum - lo) / max(hi - lo, 1), 0, 1)[..., None]
    dark = np.array([62, 44, 26], np.float32)
    mid = np.array([150, 112, 66], np.float32)
    light = np.array([222, 190, 132], np.float32)
    rgb = np.where(t < 0.5, dark + (mid - dark) * (t / 0.5), mid + (light - mid) * ((t - 0.5) / 0.5))
    out = src.copy()
    out[..., :3] = rgb
    return out


def rope_run(length, thick, period, rope):
    """A horizontal rope `length` px long, `thick` px high, its twist repeating every `period` px (seamless when
    length is a multiple of period)."""
    h, w = rope.shape[:2]
    ys = np.clip(((np.arange(thick) + 0.5) / thick * h).astype(int), 0, h - 1)
    xs = ((np.arange(length) % period) / period * w).astype(int)
    return rope[ys][:, xs].copy()


# ------------------------------------------------------------------------------------------------------------- slats
def planks():
    """The old rope deck's planks (rows between its dark gaps), each as an RGBA crop running left to right."""
    a = git_png(TEXREL + "/" + SB + "/RM_SuspensionDeck_Rope.png")
    lum = a[:, 40:216, :3].mean(axis=(1, 2))
    rows = np.where(lum > 80)[0]
    bands, start = [], rows[0]
    for p, q in zip(rows, rows[1:]):
        if q != p + 1:
            bands.append((start, p))
            start = q
    bands.append((start, rows[-1]))
    out = []
    for r0, r1 in bands:
        if r1 - r0 >= 14:
            out.append(a[r0:r1 + 1, 16:240].copy())
    return out


def slat(plank, length, width, rng):
    """One loose slat: a plank crop sized to `length` x `width` (long axis vertical), ends rounded, edges darkened."""
    p = resize(plank, length, width)                    # long axis along x
    p = np.rot90(p, 1).copy()                           # long axis vertical: shape (length, width)
    tone = rng.uniform(0.86, 1.08)
    p[..., :3] *= tone
    h, w = p.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = 4.0
    cx = np.clip(xx, r, w - 1 - r)
    cy = np.clip(yy, r, h - 1 - r)
    inside = (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r
    p[..., 3] = np.where(inside, 255, 0)
    edge = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy))
    p[..., :3] *= np.where(edge < 1.5, 0.8, np.where(edge < 3, 0.9, 1.0))[..., None]   # a soft bevel, no keyline (art_judge_brief B1a)
    return p


def lashing(width, thick, rope):
    """A wrap of rope across a slat where it sits on a side rope: three turns of real rope, slanted, over the slat."""
    W, H = width + 8, thick + 12
    lash = np.zeros((H, W, 4), np.float32)
    seg = rope_run(H + 6, 5, 18, rope)                  # a short rope piece, 5 px thick
    im = Image.fromarray(np.clip(seg + 0.5, 0, 255).astype(np.uint8), "RGBA").rotate(68, Image.BICUBIC, expand=True)
    turn = np.asarray(im, dtype=np.float32)
    for k in range(3):
        cx = 4 + (k + 0.5) * width / 3.0
        over(lash, turn, int(round(cx - turn.shape[1] / 2.0)), int(round(H / 2.0 - turn.shape[0] / 2.0)))
    return lash


def strip_piece(kind, rope, slats_src, rng):
    """One deck piece, drawn running east: two side ropes at the anchors' lateral, SLATS slats laid on them."""
    a = np.zeros((T, T, 4), np.float32)
    lat = anchor_lateral_px()
    period = T / 3.0
    run = rope_run(T, ROPE_THICK, period, rope)
    for y in (T // 2 - lat, T // 2 + lat):
        over(a, run, 0, int(round(y - ROPE_THICK / 2.0)))
    length = int(round(2 * SLAT_HALF * T))
    for k in range(SLATS):
        cx = (k + 0.5) * T / SLATS + rng.uniform(-3, 3)
        s = slat(slats_src[rng.integers(len(slats_src))], length, SLAT_W, rng)
        ang = rng.uniform(-3.5, 3.5)
        im = Image.fromarray(np.clip(s + 0.5, 0, 255).astype(np.uint8), "RGBA").rotate(ang, Image.BICUBIC, expand=True)
        s = np.asarray(im, dtype=np.float32)
        h, w = s.shape[:2]
        over(a, s, int(round(cx - w / 2.0)), int(round(T / 2.0 - h / 2.0 + rng.uniform(-2, 2))))
        for y in (T // 2 - lat, T // 2 + lat):
            lz = lashing(SLAT_W, ROPE_THICK, rope)
            over(a, lz, int(round(cx - lz.shape[1] / 2.0)), int(round(y - lz.shape[0] / 2.0)))
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)      # the game draws it Cutout: a clean edge, no grey fringe
    return a


# ------------------------------------------------------------------------------------------------------------- post
def post(rope, slats_src):
    """A hand-rope post: a round timber pole cut from the planks, shaded round, end grain on top, rope lashed under the head."""
    H, W = 400, 40
    p = slat(slats_src[2], H, W, np.random.default_rng(SEED + 7))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u = (xx + 0.5) / W
    shade = 0.5 + 0.55 * np.sqrt(np.clip(np.sin(np.pi * u), 0, 1))
    p[..., :3] *= shade[..., None]
    p[..., 3] = 255
    # end grain cap
    cap = ((xx - W / 2.0) / (W / 2.0)) ** 2 + ((yy - 8) / 7.0) ** 2 <= 1
    ring = np.sqrt(((xx - W / 2.0) / (W / 2.0)) ** 2 + ((yy - 8) / 7.0) ** 2)
    capc = np.array([176, 138, 92], np.float32) * (0.8 + 0.2 * np.cos(ring * 9))[..., None]
    p[..., :3] = np.where(cap[..., None], capc, p[..., :3])
    p[..., 3] = np.where((yy < 8) & ~cap, 0, 255)
    # foot darkened (earth)
    p[..., :3] *= np.where(yy > H - 30, 0.75, 1.0)[..., None]
    # rope lashing under the head
    for k in range(5):
        band = rope_run(W + 4, 6, 24, rope)
        over(p, band, -2, 22 + k * 7)
    p[..., 3] = np.where(p[..., 3] >= 128, 255, 0)
    return p


# ------------------------------------------------------------------------------------------------------------- anchors
def anchor_lateral_px():
    """Where the anchors' ropes run after the move, in px from the centre line (measured on the east view's top rope)."""
    a = git_png(TEXREL + "/" + SB + "/RM_SuspensionAnchor_Rope_east.png")[..., 3] > 40
    tip = np.where(a[:, T - 4])[0]
    north = tip[tip < T // 2]
    c = (north.min() + north.max()) / 2.0
    return int(round(T / 2.0 - (c + 0.5) + ANCHOR_SHIFT))


def moved_anchor(facing):
    """The anchor picture with each bollard (and its rope) moved ANCHOR_SHIFT px out from the centre line, so its rope meets
    the deck's side rope. East: the split is the row under the north rope (the south bollard rises from its rope to it)."""
    a = git_png(TEXREL + "/" + SB + "/RM_SuspensionAnchor_Rope_%s.png" % facing)
    out = np.zeros_like(a)
    d = ANCHOR_SHIFT
    if facing == "east":
        # the two bollards are one painting twice (rows 62 apart); the south one is in front, so it is whole once the north
        # bollard's base plate (wider than its head, behind it) is cut away: draw that whole south bollard at both places
        al = a[..., 3]
        full = np.where((al > 0).sum(1) > 0.6 * T)[0]
        n_rope = full[full < T // 2]
        s_rope = full[full >= T // 2]
        gap = int(round((s_rope.min() + s_rope.max()) / 2.0 - (n_rope.min() + n_rope.max()) / 2.0))
        lo = int(n_rope.max()) + 1                       # first row under the north rope
        body = np.where(al[lo + 12] > 0)[0]              # the south bollard's head columns, under its cap
        c0, c1 = int(body.min()) - 1, int(body.max()) + 1
        head = int(np.where(al.any(1))[0].min()) + gap   # the south head's top: the north head's top, one gap down
        south = a.copy()
        south[:head] = 0
        for y in range(head, lo + 10):
            south[y, :c0] = 0
            south[y, c1 + 1:] = 0
        if south[T - d:, :, 3].any() or south[:gap + d, :, 3].any():
            raise SystemExit("east: a bollard would leave the picture")
        out[d:] = south[:T - d]
        north = np.zeros_like(a)
        north[:T - gap - d] = south[gap + d:]
        over(out, north, 0, 0)
    else:
        if a[:, T // 2 - 8:T // 2 + 8, 3].any():
            raise SystemExit("%s: the centre columns are not empty" % facing)
        left, right = a[:, :T // 2], a[:, T // 2:]
        if left[:, :d, 3].any() or right[:, -d:, 3].any():
            raise SystemExit("%s: a bollard would leave the picture" % facing)
        out[:, :T // 2 - d] = left[:, d:]
        out[:, T // 2 + d:] = right[:, :T // 2 - d]
    return out


# ------------------------------------------------------------------------------------------------------------- make
def make():
    rng = np.random.default_rng(SEED)
    rope = rope_texture()
    save(rope, "RM_Cable_Rope")
    src = planks()
    pieces = {}
    for kind in ("root", "mid", "tip", "solo"):
        pieces[kind] = strip_piece(kind, rope, src, rng)
        save(pieces[kind], "RM_SuspensionDeck_Rope_Strip_" + kind)
    save(post(rope, src), "RM_SuspensionDeck_Rope_Post")
    for f in ("east", "north", "south"):
        save(moved_anchor(f), "RM_SuspensionAnchor_Rope_" + f)
    icon = np.rot90(pieces["mid"], 1).copy()             # running north, like the old icon (ropes down the sides)
    save(icon, "RM_SuspensionDeck_Rope")
    print("made rope bridge parts in", OUT, "lateral", anchor_lateral_px(), "px =", round(anchor_lateral_px() / T, 4))
    return 0


def check():
    """The parts agree: the deck ropes run where the anchors' ropes end; every piece's rope rows are continuous across the
    piece edge; slats are sparse (the walkway is mostly open between them)."""
    fails = []
    lat = anchor_lateral_px()
    for kind in ("root", "mid", "tip", "solo"):
        p = np.asarray(Image.open(os.path.join(OUT, "RM_SuspensionDeck_Rope_Strip_%s.png" % kind)))
        al = p[..., 3] > 128
        for y in (T // 2 - lat, T // 2 + lat):
            if not al[y, 0] or not al[y, T - 1]:
                fails.append("%s: the side rope at row %d does not reach both piece edges" % (kind, y))
        mid = al[T // 2 - 40:T // 2 + 40]
        open_cols = (~mid.any(0)).mean()
        if open_cols < 0.45:
            fails.append("%s: the walkway is %.0f%% open between slats, want sparse (>= 45%%)" % (kind, open_cols * 100))
    for f in ("east", "north", "south"):
        a = np.asarray(Image.open(os.path.join(OUT, "RM_SuspensionAnchor_Rope_%s.png" % f)))[..., 3] > 40
        if f == "north":
            a = np.rot90(a, -1)
        elif f == "south":
            a = np.rot90(a, 1)
        tip = np.where(a[:, T - 4])[0]
        for half in (tip[tip < T // 2], tip[tip >= T // 2]):
            c = (half.min() + half.max()) / 2.0 + 0.5
            got = abs(T / 2.0 - c)
            if abs(got - lat) > 2.5:
                fails.append("%s anchor: rope at %.1f px from the centre, the deck's at %d" % (f, got, lat))
    for m in fails:
        print("FAIL", m)
    print("rope bridge parts:", "FAIL" if fails else "PASS", "(%d faults; lateral %d px)" % (len(fails), lat))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(make() if sys.argv[1:2] == ["make"] else check() if sys.argv[1:2] == ["check"] else (print(__doc__) or 2))
