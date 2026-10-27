#!/usr/bin/env python3
"""selftest_player_truths_art.py -- the player-truth pilot's ART half (design/RimMandrake/player_truth_testing_pilot_2026-10-26.md).

Owner 2026-10-26: "The perspectives on the ladders would be the reverse of the walls they leaned on ... pipes with big
graphic gaps that didn't connect." Both were defects in the shipped PNGs, not in game logic, so these truths are swept
over every installed texture rather than over a few hand-picked cases:

  PT13 a ladder's east/west picture stands on the wall side of its cell (every ladder family; the cell spans the canvas's
       middle 2/3 at drawSize 1.5)
  PT14 a west picture is the east picture mirrored (Graphic_Multi draws each file as it is)
  PT15 a portable ladder leans INTO its wall: its top is nearer the wall than its foot (the reversed perspective)
  PT16 a pipe tile reaches every edge it links to, at the edge's middle (no gap)       } every look x all 16 link masks,
  PT17 two linked pipe tiles meet with the same cross-section across the seam         } through fw_compositor.atlas_tile,
  PT18 a pipe tile does not reach an edge it does not link to (no stub to nowhere)    } the emulation of vanilla
  PT19 a pipe tile is one piece (no floating cap or coupling)                         } SubMaterialFromAtlas

Each truth is first shown able to fail on an injected copy of the defect it guards (the probes), then run on the
installed art. Exit 0 when every truth holds on every asset; 1 lists every violation.
Usage: python3 src/RimMandrake/FlowWorks/Tools/selftest_player_truths_art.py
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fw_compositor as fc  # noqa: E402

LADDER_DIR = fc.TEX / "Things/Building/FlowWorks/Canals"
LADDER_FAMILIES = ["RM_Ladder", "RM_LadderRaised", "RM_LadderSteel", "RM_LadderSteelRaised", "RM_LadderPortable"]
PIPE_LOOKS = ["Modern", "Industrial", "Futuristic", "Scrapper"]
DRAW_SIZE = 1.5          # every ladder's drawSize (FlowWorks_ThingDefs.xml, FlowWorks_PitAccess.xml)
OPAQUE = 128
N, E, S, W = 1, 2, 4, 8  # vanilla LinkDirections bits


def alpha(img):
    return np.asarray(img.convert("RGBA"))[:, :, 3] > OPAQUE


def centroid_x(a, rows=None):
    sub = a if rows is None else a[rows]
    ys, xs = np.nonzero(sub)
    return float(xs.mean()) if xs.size else float("nan")


# ── ladders ──────────────────────────────────────────────────────────

def ladder_cell(width):
    """(left, right) pixel columns of the ladder's own cell on its canvas."""
    span = width / DRAW_SIZE
    return (width - span) / 2, (width + span) / 2


def ladder_truths(east, west, family, portable):
    """Violations (strings) of PT13-PT15 for one family's east and west pictures."""
    bad = []
    ae, aw = alpha(east), alpha(west)
    width = ae.shape[1]
    left, right = ladder_cell(width)
    mid = (left + right) / 2
    quarter = (right - left) / 4
    ce, cw = centroid_x(ae), centroid_x(aw)
    # PT13: the picture's mass lies in the wall-side half of the cell, not across it
    if not (mid + 0.1 * quarter < ce <= right):
        bad.append("PT13 %s_east: mass at x %.0f, the east (wall) half of the cell is x %.0f-%.0f" % (family, ce, mid, right))
    if not (left <= cw < mid - 0.1 * quarter):
        bad.append("PT13 %s_west: mass at x %.0f, the west (wall) half of the cell is x %.0f-%.0f" % (family, cw, left, mid))
    # PT14: west is east mirrored
    flipped = np.asarray(ae[:, ::-1])
    inter, union = np.logical_and(flipped, aw).sum(), np.logical_or(flipped, aw).sum()
    iou = inter / union if union else 0.0
    if iou < 0.85:
        bad.append("PT14 %s: west vs mirrored east overlap %.2f (want >= 0.85)" % (family, iou))
    # PT15: a leaning ladder's top is nearer its wall than its foot
    if portable:
        ys = np.nonzero(ae.any(axis=1))[0]
        top, foot = slice(ys.min(), ys.min() + (ys.max() - ys.min()) // 4), slice(ys.max() - (ys.max() - ys.min()) // 4, ys.max() + 1)
        te, fe = centroid_x(ae, top), centroid_x(ae, foot)
        ys = np.nonzero(aw.any(axis=1))[0]
        top, foot = slice(ys.min(), ys.min() + (ys.max() - ys.min()) // 4), slice(ys.max() - (ys.max() - ys.min()) // 4, ys.max() + 1)
        tw, fw = centroid_x(aw, top), centroid_x(aw, foot)
        if not te > fe + 0.25 * quarter:
            bad.append("PT15 %s_east: top at x %.0f, foot at x %.0f: it leans away from its east wall" % (family, te, fe))
        if not tw < fw - 0.25 * quarter:
            bad.append("PT15 %s_west: top at x %.0f, foot at x %.0f: it leans away from its west wall" % (family, tw, fw))
    return bad


def load_ladder(family, facing):
    return Image.open(LADDER_DIR / ("%s_%s.png" % (family, facing)))


# ── pipes ────────────────────────────────────────────────────────────

def edge_strip(a, d, k=2):
    """The outermost k pixels on side d (image rows run north to south)."""
    return {N: a[:k, :], S: a[-k:, :], E: a[:, -k:].T, W: a[:, :k].T}[d]


def edge_line(a, d):
    return {N: a[0, :], S: a[-1, :], E: a[:, -1], W: a[:, 0]}[d]


def pieces(a, min_frac=0.005):
    """8-connected pieces of the opaque pixels, ignoring specks under min_frac of the tile."""
    h, w = a.shape
    seen = np.zeros_like(a, bool)
    out = []
    for y0, x0 in zip(*np.nonzero(a)):
        if seen[y0, x0]:
            continue
        stack, n = [(y0, x0)], 0
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            n += 1
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < h and 0 <= xx < w and a[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        stack.append((yy, xx))
        if n >= min_frac * h * w:
            out.append(n)
    return out


def pipe_truths(tiles, look):
    """Violations of PT16-PT19 over one look's 16 tiles (dict mask -> opaque bool array)."""
    bad = []
    opp = {N: S, S: N, E: W, W: E}
    for m in range(16):
        a = tiles[m]
        L = a.shape[0]
        bore = max(1, int(tiles[5][L // 2].sum()))          # the pipe's own width: the N-S straight across its middle
        lo, hi = int(L * 0.2), int(L * 0.8)
        for d, name in ((N, "N"), (E, "E"), (S, "S"), (W, "W")):
            strip = edge_strip(a, d).any(axis=0)
            if m & d:
                run = strip[lo:hi].sum()
                if run < 0.6 * bore:
                    bad.append("PT16 %s mask %d: links %s but only %d px of a %d px pipe reach that edge's middle" % (look, m, name, run, bore))
            else:
                line = edge_line(a, d)
                if line.sum() > 0.02 * L:
                    bad.append("PT18 %s mask %d: does not link %s but %d px of pipe touch that edge" % (look, m, name, line.sum()))
        p = pieces(a)
        if len(p) != 1:
            bad.append("PT19 %s mask %d: %d separate pieces (sizes %s)" % (look, m, len(p), sorted(p, reverse=True)[:4]))
    for d, name in ((E, "E-W"), (N, "N-S")):
        for m in range(16):
            if not m & d:
                continue
            for n in range(16):
                if not n & opp[d]:
                    continue
                x, y = edge_line(tiles[m], d), edge_line(tiles[n], opp[d])
                union = np.logical_or(x, y).sum()
                iou = np.logical_and(x, y).sum() / union if union else 0.0
                if iou < 0.85:                                   # 18 px bore: a 1 px jog reads 0.89, 2 px 0.80, 3 px 0.71
                    jog = abs(np.nonzero(x)[0].mean() - np.nonzero(y)[0].mean()) if x.any() and y.any() else float("nan")
                    bad.append("PT17 %s seam %s, mask %d beside mask %d: cross-sections overlap %.2f, centres %.1f px apart (want >= 0.85)"
                               % (look, name, m, n, iou, jog))
    return bad


def look_tiles(look):
    atlas = fc.pipe_atlas(look)
    return {m: alpha(fc.atlas_tile(atlas, m)) for m in range(16)}


# ── probes: every truth fails on its own defect ──────────────────────

def probes():
    fails = []
    e, w = load_ladder("RM_LadderPortable", "east"), load_ladder("RM_LadderPortable", "west")
    swapped = ladder_truths(w, e, "probe", True)            # the reversed perspective: east and west exchanged
    if not any(s.startswith("PT13") for s in swapped) or not any(s.startswith("PT15") for s in swapped):
        fails.append("probe: east/west swapped is not caught by PT13 and PT15: %s" % swapped)
    ae = np.asarray(e.convert("RGBA")).copy()
    shift = int(ae.shape[1] / DRAW_SIZE / 2)                 # the first fix: right lean, far side of the cell
    moved = np.zeros_like(ae)
    moved[:, : ae.shape[1] - shift] = ae[:, shift:]
    far = ladder_truths(Image.fromarray(moved), ImageOps.mirror(Image.fromarray(moved)), "probe", True)
    if not any(s.startswith("PT13") for s in far):
        fails.append("probe: the far-side ladder (east picture half a cell west) is not caught by PT13")
    wrong_mirror = ladder_truths(e, e, "probe", True)
    if not any(s.startswith("PT14") for s in wrong_mirror):
        fails.append("probe: west == east (not mirrored) is not caught by PT14")
    tiles = look_tiles("Modern")
    gap = dict(tiles)
    a = gap[5].copy()                                        # N+S straight with its north end cut short: a gap
    a[: a.shape[0] // 4, :] = False
    gap[5] = a
    if not any(s.startswith("PT16 probe mask 5") for s in pipe_truths(gap, "probe")):
        fails.append("probe: a straight cut short of its north edge is not caught by PT16")
    shifted = dict(tiles)
    b = np.zeros_like(tiles[10])                             # E+W straight drawn a fifth of a tile off-centre
    off = tiles[10].shape[0] // 5
    b[off:, :] = tiles[10][:-off, :]
    shifted[10] = b
    if not any(s.startswith("PT17 probe seam E-W, mask 10") for s in pipe_truths(shifted, "probe")):
        fails.append("probe: an off-centre straight is not caught by PT17")
    stub = dict(tiles)
    c = tiles[0].copy()                                      # an isolated pipe with an arm out to its east edge
    mid = c.shape[0] // 2
    c[mid - 4: mid + 4, c.shape[1] // 2:] = True
    stub[0] = c
    if not any(s.startswith("PT18 probe mask 0: does not link E") for s in pipe_truths(stub, "probe")):
        fails.append("probe: an arm to an unlinked edge is not caught by PT18")
    floating = dict(tiles)
    f = tiles[5].copy()
    side = int(f.shape[0] * 0.12)                            # a detached square in the corner, above the speck floor
    f[2:2 + side, 2:2 + side] = True
    floating[5] = f
    if not any(s.startswith("PT19 probe mask 5") for s in pipe_truths(floating, "probe")):
        fails.append("probe: a detached piece is not caught by PT19")
    return fails


def main():
    fails = probes()
    print("probes: %s" % ("every truth fails on its own defect" if not fails else "%d BLIND" % len(fails)))
    for f in fails:
        print("  " + f)
    bad, swept = [], 0
    for fam in LADDER_FAMILIES:
        swept += 1
        bad += ladder_truths(load_ladder(fam, "east"), load_ladder(fam, "west"), fam, fam == "RM_LadderPortable")
    for look in PIPE_LOOKS:
        swept += 16
        bad += pipe_truths(look_tiles(look), look)
    print("swept %d ladder families x E/W and %d pipe looks x 16 masks (%d assets)" % (len(LADDER_FAMILIES), len(PIPE_LOOKS), swept))
    for truth in ("PT13", "PT14", "PT15", "PT16", "PT17", "PT18", "PT19"):
        mine = [b for b in bad if b.startswith(truth)]
        print("%s: %s" % (truth, "holds" if not mine else "%d violations" % len(mine)))
        for b in mine[:12]:
            print("  " + b)
        if len(mine) > 12:
            print("  ... %d more" % (len(mine) - 12))
    return 0 if not fails and not bad else 1


if __name__ == "__main__":
    sys.exit(main())
