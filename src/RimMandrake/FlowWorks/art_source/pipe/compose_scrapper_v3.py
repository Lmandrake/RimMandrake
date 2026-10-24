#!/usr/bin/env python3
"""SCRAPPER_PIPE_REDRAW_BLURRY_AT_ZOOM + SCRAPPER_PIPE_REDRAW_ASKED_TWICE_NOW: the Scrapper UniversalPipe atlas v3.

Owner 2026-10-23: "scavver pipe is VERY low res, please use higher resolution graphics" / "ugly as heck ... low res" (a long
straight run reads thin, soft and repeats the same green spot every cell). Judge-seat measurement (ledger note, 05:40Z): v2
lost its detail in compose_scrapper_v2.strip_period() -- the raw tube averaged with its vertical flip (cancels every
asymmetric mark), shrunk to 18 px and its broad colour damped; edge contrast 7.8-10.9 against Industrial 12-21.

v3 keeps v2's geometry exactly (build_pipe_atlas.tile_for: pipe on the tile centre, elbow r = C/2 about the SHOWN cell
corner, rot90 turns) but:
  * authors at 2x: 1408 px atlas, 352 px tile, 264 px shown per cell, pipe 36 px (0.136 cell, as every look), hub 88 px,
    cap collar 64 px. Graphic_Linked addresses an atlas by UV fraction, so its pixel size is the look's own business;
  * symmetrises only what must be symmetric. Every turn is a rot90, so a tube meets a neighbour turned 180 degrees across
    its axis -- but only AT THE CELL EDGE. So the cross-section shading profile (the per-row median, a 1-D curve) is made
    mirror-symmetric, and the full tube is blended toward its mirror only inside SEAM px of each cell edge; every dent,
    fleck and scratch in between is kept as generated (v2 averaged the whole tube with its flip);
  * keeps the colour as generated (no broad damping): the per-cell repeat is broken by straight-run variants instead;
  * centres the boss: v2 resized its boss to 44 px but tile_for placed it with build_pipe_atlas.HUB = 36, so every
    junction and the lone stub sat 4 px south-east of the pipe axis. v3 sets the module's HUB to the boss it draws;
  * writes Pipe/Scrapper/UniversalPipe_Straights.png: NV straight-run variants (column k-1 = variant k; row 0 east-west,
    row 1 north-south), each tile laid out like an atlas tile (T x T, the shown C x C inside P px of padding). Their ends
    cross-fade into the base period over ENDS px, so any variant joins the atlas pipe (and each other) pixel-identically;
    the draw picks one per straight cell by a stable cell hash (Machinery/PipeStraightVariants.cs).

Sources (codex image_gen 2026-10-23):
  raw/scrapper_v3_strips.png     three horizontal scavenged copper pipes: plain / twisted-wire wrap + hose clamp / riveted
                                 sheet patch with odd bolts;
  raw/scrapper_v3_fittings.png   LEFT a round boss of mismatched scrap (steel ring, dented copper dome, hex/square/wing
                                 fasteners, welded strap), RIGHT a capped pipe end (hose-clamp collar, wire twist, bolted dome).

Usage: compose_scrapper_v3.py [--install]   (writes out/Scrapper_v3_*.png; --install goes through the art ledger)
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_pipe_atlas as B  # noqa: E402  (geometry: tile_for, over, premul_resize; scaled below)

SCALE = 2
T = B.T * SCALE            # 352
P = T // 8                 # 44
C = T - 2 * P              # 264 px shown per cell
W_PIPE = B.W_PIPE * SCALE  # 36
HUB = 44 * SCALE           # 88: v2's boss share of the cell (0.33)
CAP_H = 32 * SCALE         # 64: cap collar height (Industrial/Modern 32 at 1x)
XFADE = 16                 # px: period wrap cross-fade
SEAM = 24                  # px each side of a cell edge blended toward the axis mirror
ENDS = 40                  # px at each end of a variant cross-faded into the base period
NV = 4                     # straight-run variants besides the atlas's own straight (PipeStraightVariants.Count)


def scaled_geometry():
    """build_pipe_atlas's module constants at 2x: tile_for / h_run read them as globals at call time."""
    B.T, B.P, B.C, B.W_PIPE, B.HUB, B.ATLAS = T, P, C, W_PIPE, HUB, 4 * T


def pipe_bands():
    """The three generated pipes, top to bottom: (tube_top, tube_bottom) rows of each, from the rows the tube fills
    edge to edge (>60% of the width opaque), in the raw strip sheet."""
    s = B.load(HERE / "raw" / "scrapper_v3_strips.png")
    full = (s[..., 3] > 0.5).mean(1) > 0.6
    rows = np.where(full)[0]
    runs = np.split(rows, np.where(np.diff(rows) > 1)[0] + 1)
    runs = [r for r in runs if len(r) > 40]
    assert len(runs) == 3, "expected three pipes, found %d" % len(runs)
    return s, [(int(r[0]), int(r[-1]) + 1) for r in runs]


def tube(s, top, bot, margin):
    """One pipe scaled so its tube is W_PIPE px tall, with `margin` scaled px of rows above and below for hardware.
    The cross-section shading profile is made mirror-symmetric; surface detail is kept."""
    h = bot - top
    k = W_PIPE / h
    m_raw = int(round(margin / k))
    y0, y1 = max(0, top - m_raw), min(s.shape[0], bot + m_raw)
    crop = s[y0:y1].copy()
    # symmetric profile from the tube rows only (median over columns: hardware is a minority of columns)
    t0, t1 = top - y0, bot - y0
    tb = crop[t0:t1]
    prof = np.median(tb[..., :3], axis=1, keepdims=True)
    tb[..., :3] = np.clip(tb[..., :3] + 0.5 * (prof[::-1] - prof), 0, 1)
    crop[t0:t1] = tb
    L = int(round(crop.shape[1] * k))
    H = W_PIPE + 2 * margin
    out = B.premul_resize(crop, (L, int(round(crop.shape[0] * k))))
    full = np.zeros((H, L, 4), np.float32)          # place so the tube sits exactly on rows margin..margin+W_PIPE
    oy = margin - int(round((top - y0) * k))
    ys0, ys1 = max(0, -oy), min(out.shape[0], H - oy)
    full[oy + ys0:oy + ys1] = out[ys0:ys1]
    tb = full[margin:margin + W_PIPE]
    tb[..., 3] = np.where(tb[..., 3] > 0.5, 1.0, tb[..., 3])       # solid body, soft outline kept
    return full


def seamless(seg):
    """A (C + XFADE)-wide window made into one wrap-seamless C-px period (overrun cross-faded into its head)."""
    w = np.linspace(0, 1, XFADE, dtype=np.float32)[None, :, None]
    seg = seg.copy()
    seg[:, :XFADE] = seg[:, C:C + XFADE] * (1 - w) + seg[:, :XFADE] * w
    return seg[:, :C]


def seam_symmetric(per):
    """Blend the period toward its axis mirror near phase 0 (both cell edges): weight 1 on the 3 edge columns, 0 at SEAM+3 px."""
    u = np.arange(C)
    d = np.minimum(u + 0.5, C - u - 0.5)
    w = np.clip(1 - (d - 3) / SEAM, 0, 1)[None, :, None] ** 0.7    # exactly mirror-symmetric on the 3 edge columns
    out = per * (1 - w) + 0.5 * (per + per[::-1]) * w
    # tile_for's elbow arc samples phase C-1 on its edge column where a straight samples phase 0 (floor of C - eps);
    # at 2x grain that one-column step shows as a seam, so the last column repeats the first
    out[:, C - 1] = out[:, 0]
    return out


def periods():
    """(base, [variant 1..NV]): base is W_PIPE x C (the atlas strip); variants are (W_PIPE + 2*VM) x C with the tube on
    rows VM..VM+W_PIPE and their ends equal to the base's."""
    s, bands = pipe_bands()
    plain = tube(s, *bands[0], margin=0)
    x0 = int(0.18 * (plain.shape[1] - C - XFADE))
    base = seam_symmetric(seamless(plain[:, x0:x0 + C + XFADE]))
    vm = VM
    vars_ = []
    # variants 1, 2: other stretches of the plain pipe (one run the other way), so its blotches land elsewhere in the cell
    p1 = tube(s, *bands[0], margin=vm)
    for frac, flip in ((0.82, True), (0.50, False)):
        xa = int(frac * (p1.shape[1] - C))
        v = p1[:, xa:xa + C][:, ::-1] if flip else p1[:, xa:xa + C][::-1].copy()   # second: mirrored across the axis
        v[:vm] = 0; v[vm + W_PIPE:] = 0                                             # plain pipe: nothing in the margins
        if not flip:
            weld_seam(v, vm, int(0.30 * C))      # art-eval round 2: plain runs need a little salvage character
        vars_.append(v)
    # variants 3, 4: the repair hardware (the columns whose opaque height exceeds the tube's) placed off-centre at `at`
    for bi, at in ((1, 0.42), (2, 0.58)):
        p = tube(s, *bands[bi], margin=vm)
        hgt = (p[..., 3] > 0.5).sum(0)
        hw = np.where(hgt > W_PIPE * 1.06)[0]
        cx = int((hw.min() + hw.max()) / 2) if len(hw) else p.shape[1] // 2
        xa = int(np.clip(cx - int(at * C), 0, p.shape[1] - C))
        v = p[:, xa:xa + C].copy()
        keep = np.zeros(C, bool)                                    # margins keep only the hardware's own columns
        h = hw - xa; h = h[(h >= 0) & (h < C)]
        if len(h): keep[max(0, h.min() - 4):min(C, h.max() + 5)] = True
        v[:vm, ~keep] = 0; v[vm + W_PIPE:, ~keep] = 0
        vars_.append(attached_only(v, vm))
    bpad = np.zeros((W_PIPE + 2 * vm, C, 4), np.float32)
    bpad[vm:vm + W_PIPE] = base
    u = np.arange(C)
    w = np.clip(np.minimum(u, C - 1 - u) / float(ENDS), 0, 1)[None, :, None]
    w = w * w * (3 - 2 * w)                                        # smoothstep: base at the edges, variant mid-cell
    out = []
    for v in vars_:
        mix = premul_mix(bpad, v, w)
        out.append(mix)
    return base, out


def weld_seam(v, vm, cx):
    """A crude field weld across the tube at column cx (in place): a scorched ring either side of a bright, lumpy
    bead, shaded by the tube's own light so it stays round. Rows vm..vm+W_PIPE are the tube."""
    rows = slice(vm, vm + W_PIPE)
    rng = np.random.default_rng(7)
    for dx, gain in ((-4, 0.70), (-3, 0.55), (-2, 0.62), (-1, 1.18), (0, 1.32), (1, 1.25), (2, 0.62), (3, 0.55), (4, 0.72)):
        col = v[rows, cx + dx, :3]
        lum = col.mean(1, keepdims=True)
        if gain > 1:                                       # bead: greyed toward bright steel, a little lumpy
            jit = 1 + 0.08 * rng.standard_normal((W_PIPE, 1))
            col[:] = np.clip((0.45 * col + 0.55 * lum) * gain * jit, 0, 1)
        else:
            col[:] = col * gain


def attached_only(v, vm):
    """Clear every margin pixel not 8-connected to the tube rows through visible alpha (art-eval round 1 of v3 found
    detached specks beside the patch plate: ALPHA_HALO). No scipy here, so the fill is repeated one-pixel dilation."""
    vis = v[..., 3] > 0.02
    reach = np.zeros_like(vis)
    reach[vm:vm + W_PIPE] = vis[vm:vm + W_PIPE]
    while True:
        g = reach.copy()
        g[1:] |= reach[:-1]; g[:-1] |= reach[1:]
        g[:, 1:] |= g[:, :-1].copy(); g[:, :-1] |= g[:, 1:].copy()
        g &= vis
        if (g == reach).all():
            break
        reach = g
    out = v.copy()
    out[~reach] = 0
    return out


VM = 14                    # px of hardware margin above/below a variant's tube (clamp screw, wire end)


def premul_mix(a, b, w):
    """a*(1-w) + b*w in premultiplied space (so a fading-in transparent pixel does not drag colour)."""
    pa = a[..., :3] * a[..., 3:4]; pb = b[..., :3] * b[..., 3:4]
    al = a[..., 3:4] * (1 - w) + b[..., 3:4] * w
    rgb = (pa * (1 - w) + pb * w) / np.maximum(al, 1e-5)
    return np.concatenate([np.where(al > 1e-5, rgb, 0), al], -1)


def fittings():
    f = B.load(HERE / "raw" / "scrapper_v3_fittings.png")
    a = f[..., 3] > 0.5
    xs = np.where(a.any(0))[0]
    gap = np.where(np.diff(xs) > 8)[0][0]
    hub = f[:, xs[0]:xs[gap] + 1]; cap = f[:, xs[gap + 1]:xs[-1] + 1]
    ha = hub[..., 3] > 0.5
    rr = np.where(ha.any(1))[0]; cc = np.where(ha.any(0))[0]
    hub = hub[rr[0]:rr[-1] + 1, cc[0]:cc[-1] + 1]
    side = max(hub.shape[:2])                                         # pad to square about its own centre
    sq = np.zeros((side, side, 4), np.float32)
    oy, ox = (side - hub.shape[0]) // 2, (side - hub.shape[1]) // 2
    sq[oy:oy + hub.shape[0], ox:ox + hub.shape[1]] = hub
    hub = B.premul_resize(sq, (HUB, HUB))
    ca = cap[..., 3] > 0.5
    rr = np.where(ca.any(1))[0]; cc = np.where(ca.any(0))[0]
    cap = cap[rr[0]:rr[-1] + 1, cc[0]:cc[-1] + 1]
    ca = cap[..., 3] > 0.5
    colh = ca.sum(0)
    stub = np.median(colh[: len(colh) // 4])
    tall = np.where(colh > 1.15 * stub)[0]
    cap = cap[:, max(0, tall[0] - 8):]                                # collar + dome; the atlas draws the pipe itself
    k = CAP_H / cap.shape[0]
    cap = B.premul_resize(cap, (max(1, int(round(cap.shape[1] * k))), CAP_H))
    # art-eval round 2: the dome's two coloured bolt heads (one rust-red, one brass) read as a face on a north cap; pull the
    # dome's warm pixels toward its own steel grey so they read as plain bolts
    dome = cap[:, int(cap.shape[1] * 0.55):]
    rgb = dome[..., :3]
    lum = rgb.mean(-1, keepdims=True)
    warm = ((rgb[..., 0] > rgb[..., 1] * 1.15) & (rgb[..., 0] > rgb[..., 2] * 1.3))[..., None]
    rgb[:] = np.where(warm, 0.25 * rgb + 0.75 * lum * np.array([1.0, 0.98, 0.95], np.float32), rgb)
    return hub, cap


def straight_tile(per, horizontal):
    """A T x T tile carrying one straight run at the atlas phase (tile x -> (x - P) mod C), like tile_for's 5 / 10."""
    h = per.shape[0]
    t = np.zeros((T, T, 4), np.float32)
    idx = (np.arange(T) - P) % C
    B.over(t, per[:, idx], 0, P + C // 2 - h // 2)
    return t if horizontal else np.rot90(t, -1)


def to_img(arr):
    a = (np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8)
    a[a[..., 3] < 8] = 0
    return Image.fromarray(a, "RGBA")


def build():
    scaled_geometry()
    base, variants = periods()
    hub, cap = fittings()
    atlas = np.zeros((4 * T, 4 * T, 4), np.float32)
    for i in range(16):
        col, row_b = i % 4, i // 4
        r = 3 - row_b
        atlas[r * T:(r + 1) * T, col * T:(col + 1) * T] = B.tile_for(i, base, hub, cap)
    sheet = np.zeros((2 * T, NV * T, 4), np.float32)
    for k, v in enumerate(variants):
        sheet[0:T, k * T:(k + 1) * T] = straight_tile(v, True)
        sheet[T:2 * T, k * T:(k + 1) * T] = straight_tile(v, False)
    return to_img(atlas), to_img(sheet)


def menu_icon(img):
    def inner(i):
        col, row_b = i % 4, i // 4; r = 3 - row_b
        return img.crop((col * T + P, r * T + P, col * T + P + C, r * T + P + C))
    ic = Image.new("RGBA", (3 * C, 3 * C), (0, 0, 0, 0))
    for (i, x, y) in [(4, 1, 0), (2, 0, 1), (15, 1, 1), (8, 2, 1), (1, 1, 2)]:
        ic.alpha_composite(inner(i), (x * C, y * C))
    bb = ic.getbbox(); side = max(bb[2] - bb[0], bb[3] - bb[1]) + 8
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.alpha_composite(ic.crop(bb), ((side - (bb[2] - bb[0])) // 2, (side - (bb[3] - bb[1])) // 2))
    arr = (B.premul_resize(np.asarray(sq).astype(np.float32) / 255, (128, 128)) * 255 + 0.5).astype(np.uint8)
    arr[..., 3] = np.where(arr[..., 3] < 32, 0, arr[..., 3])
    arr[arr[..., 3] == 0] = 0
    return Image.fromarray(arr, "RGBA")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true")
    a = ap.parse_args()
    B.OUT.mkdir(exist_ok=True)
    atlas, sheet = build(); icon = menu_icon(atlas)
    outs = (("UniversalPipe_Atlas", atlas), ("UniversalPipe_Straights", sheet), ("UniversalPipe_MenuIcon", icon))
    for name, im in outs:
        im.save(B.OUT / f"Scrapper_v3_{name}.png")
        print("built", B.OUT / f"Scrapper_v3_{name}.png", im.size)
    if a.install:
        sys.path.insert(0, str(B.REPO / "src/RimMandrake/Utils/art"))
        import artledger as L
        why = "script:src/RimMandrake/FlowWorks/art_source/pipe/compose_scrapper_v3.py"
        for name, im in outs:
            print("  ", L.install_image(B.TEX / "Scrapper" / f"{name}.png", im, reason=why,
                                        provenance={"kind": "derived", "job": "pipe_scrapper_v3"}))


if __name__ == "__main__":
    main()
