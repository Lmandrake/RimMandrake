#!/usr/bin/env python3
"""Machine checks on fw_compositor renders: each owner-found art defect becomes a permanent check that reads the picture
(or the draw list behind it), proven to FAIL on the art he rejected and PASS on the fix. The pipe-join checks read
fw_scenes_pipejoins' Python EMULATION of the shipped (before) and fixed (after) C# draw code, tied to the C# only by the
selftest's parity constants and the C# SelfTest (e.g. ReelRiserShadowChecks for LiquidJoinRule.TravelsWest); the
sprinkler and ladder checks read the real installed PNGs (selftest_fw_offline_art.py runs
them nightly through run_selftests.py). Owner 2026-10-24: "Please find ways to test for those defects in your own offline
and in-game testing from now on, so we don't repeat mistakes."

Pipe joins (PIPE_JOINS_REDRAW_RISER_ELBOW_AND_COLLAR; his words: "The collar by the tank is superimposed and odd. the
corner has no treatment at all in the north. In the south there is a crude "cap" graphic that's inappropriate"):
  collar_on_riser    no Flange pixel is drawn on a pipe that rises into a tank's own drawn nozzle
  end_cap_on_riser   no dead-end atlas tile (0 or 1 arm) on a cell whose pipe carries on into a tank
  riser_kinks        every riser turns smoothly: heading changes by at most 2 degrees where two pieces meet
  riser_gaps         the riser's centreline is drawn pipe all the way from the cell to the port (no hole)
  riser_rims_north   the bent strip keeps the straight tile's north rim on the north, both sides of a tank

Sprinkler head (SPRINKLER_SEAT_FIX_HEAD_BESIDE_ELBOW; his words: "their alignment still reads poorly, need adjustment
onto the pipe ... make the sprinkler object be shorter, squatter, and wider so that it looks ok over any pipe"):
  head_centroid_on_axis  the head's drawn mass sits on the pipe's drawn centreline: within HEAD_TOL cell across and along,
                         on N/S, E/W, every elbow, end, tee and cross (a tall head's mass floats north of an E/W pipe)
  head_clamp_straddles_pipe  centred across on the seat within half a bore, clamp's lowest row 0.03-0.15 cell south of it
  head_squat             drawn no taller than wide, and at least 2.5 bore widths wide so it straddles any pipe
  head_seat_on_pipe      the seat point (cell centre + RM_PipeSeatMath) lands on drawn pipe (within half a bore); seat MATH
                         only, it reads no head pixel (the art's seat row is pinned by the selftest's drawOffset parity)
Portable ladder (LADDER_PORTABLE_REDRAW_NORTH_FROM_GROUND; his words: "the one laying on its side looks really good" /
"yes I'd like to see the ground portable ladder used"; south "only small nubs sticking up"):
  ladder_north_not_compressed  keeps the ground ladder's length/width and rung pitch/stringer span (0.92x..1.09x), >= 0.85 cell
                               long, top poking past the far rim and foot on the face (placement, not just shape)
  ladder_south_footprint       two or more small nubs standing on the near rim: area, height and foot row bounded
Each returns (ok, detail).
"""
import math

import numpy as np

import fw_compositor as fc


def _popcount(m):
    return bin(m & 15).count("1")


def collar_on_riser(scene):
    if not scene.risers:
        return False, "no risers in scene (nothing to measure)"
    im = np.asarray(scene.render(only=lambda m: m.get("kind") == "flange" and m.get("riser")))
    n = int((im[..., 3] > 32).sum())
    return n == 0, "%d flange pixels on riser pipes" % n


def end_cap_on_riser(scene):
    if not scene.risers:
        return False, "no risers in scene (nothing to measure)"
    bad = sorted({(m["cell"], m["mask"]) for _, _, _, m in scene.draws
                  if m and m.get("kind") == "tile" and m.get("riser") and _popcount(m["mask"]) <= 1})
    return not bad, "dead-end tiles on riser cells: %s" % (bad or "none")


def _heading(seg, f):
    if seg[0] == "L":
        return math.degrees(math.atan2(seg[4] - seg[2], seg[3] - seg[1]))
    _, _, _, _, a0, sw = seg
    return a0 + sw * f + (90 if sw > 0 else -90)


def riser_kinks(scene, tol=2.0):
    if not scene.risers:
        return False, "no risers in scene (nothing to measure)"
    worst, where = 0.0, None
    for cell, path in scene.risers:
        for a, b in zip(path, path[1:]):
            d = abs((_heading(b, 0) - _heading(a, 1) + 180) % 360 - 180)
            if d > worst:
                worst, where = d, cell
    return worst <= tol, "sharpest turn %.1f deg (cell %s)" % (worst, where)


def riser_gaps(scene, step=0.03, need=1.0):
    if not scene.risers:
        return False, "no risers in scene (nothing to measure)"
    im = np.asarray(scene.render(only=lambda m: m.get("kind") in ("tile", "strip", "stub")))
    H, W = im.shape[:2]
    worst, where = 1.0, None
    for cell, path in scene.risers:
        hit = tot = 0
        for seg in path:
            L = (math.hypot(seg[3] - seg[1], seg[4] - seg[2]) if seg[0] == "L" else abs(math.radians(seg[5])) * seg[3])
            k = max(2, int(L / step))
            for i in range(k):
                x, z = fc.seg_end(seg, (i + 0.5) / k)   # interior samples: a path's last pixel may round off its end
                px, py = scene.to_px(x, z)
                ix, iy = min(W - 1, max(0, int(px))), min(H - 1, max(0, int(py)))
                tot += 1
                hit += im[iy, ix, 3] > 128
        f = hit / max(1, tot)
        if f < worst:
            worst, where = f, cell
    return worst >= need, "least-drawn riser centreline %.0f%% (cell %s)" % (worst * 100, where)


def _probe_tile(n=64):
    """A test cross-section: the north half red, the south half blue (every pipe look's straight tile is near mirror-
    symmetric across the bore, so the real art cannot show a flipped strip; this tile can)."""
    a = np.zeros((n, n, 4), np.uint8)
    a[: n // 2, :, 0] = 255
    a[n // 2:, :, 2] = 255
    a[..., 3] = 255
    return fc.Image.fromarray(a, "RGBA")


def riser_rims_north(scene, half_w=0.12):
    """Each riser strip, re-drawn on its own path with the orientation the scene actually DREW it with (meta west_drawn,
    set by Scene.strip) but a red-north/blue-south test tile: on the level run into the tank, red must be on the north
    side of the centreline and blue on the south. A strip with no riser record or no west_drawn tag is a failure.
    Scope: on an emulated scene whose strips take Scene.strip's default this verifies the emulation's own rule
    (fw_compositor.travels_west) end to end; it catches a scene that forces the wrong west= (the review's flip). The C#
    rule LiquidJoinRule.TravelsWest is held by the in-game SelfTest, not here."""
    probe = _probe_tile()
    bad, n = [], 0
    for _, _, _, m in scene.draws:
        if not m or m.get("kind") != "strip":
            continue
        if not 0 <= m.get("id", -1) < len(scene.risers) or "west_drawn" not in m:
            bad.append(("untracked strip", m.get("id")))
            continue
        cell, path = scene.risers[m["id"]]
        seg = path[-1]
        if seg[0] != "L" or abs(seg[4] - seg[2]) > 1e-9 or abs(seg[3] - seg[1]) < 0.1:
            continue
        t = fc.Scene(scene.w, scene.h, px=scene.P, ground=False)
        t.strip(probe, path, half_w=half_w, west=m["west_drawn"], meta={"kind": "probe"})
        im = np.asarray(t.render(only=lambda q: True), np.int32)
        H, W = im.shape[:2]
        x = (seg[1] + seg[3]) / 2
        pts = [tuple(map(int, t.to_px(x, seg[2] + s * half_w * 0.5))) for s in (1, -1)]
        if any(not (0 <= px < W and 0 <= py < H) for px, py in pts):
            bad.append(("probe off canvas", cell))
            continue
        (nx, ny), (sx, sy) = pts
        north, south = im[ny, nx], im[sy, sx]
        n += 1
        if not (north[0] > north[2] and south[2] > south[0]):
            bad.append(cell)
    return n > 0 and not bad, "%d runs probed; north rim on the south at %s" % (n, bad or "none")


PIPE_JOIN_CHECKS = (collar_on_riser, end_cap_on_riser, riser_kinks, riser_gaps, riser_rims_north)


# ---- sprinkler head (scenes: fw_scenes_sprinkler.board) --------------------------------------------------------------
HEAD_TOL = 0.13      # cell: how far the head's alpha-weighted centre may sit from the drawn pipe centreline
BORE = 0.136         # cell: the universal pipe's bore width, every look (measured; fw_scenes_pipejoins.BORE_HALF)


def _heads(scene):
    return [m for _, _, _, m in scene.draws if m and m.get("kind") == "head"]


def _alpha(scene, meta):
    return np.asarray(scene.render(only=lambda m: m is meta))[..., 3].astype(float)


def head_centroid_on_axis(scene, tol=HEAD_TOL):
    """Coarse: the head's alpha-weighted centre within tol of the seat (a tall head's mass floats north). Lopsided by design
    (the squat dome sits ~0.1 cell north of its seat), so head_clamp_straddles_pipe carries the exact placement."""
    heads = _heads(scene)
    if not heads:
        return False, "no head drawn"
    worst, where = 0.0, None
    for m in heads:
        a = _alpha(scene, m)
        ys, xs = np.nonzero(a > 40)
        if not len(xs):
            return False, "head at mask %s draws no opaque pixel" % m["mask"]
        w = a[ys, xs]
        cx = (xs * w).sum() / w.sum() / scene.P
        cz = scene.h - (ys * w).sum() / w.sum() / scene.P
        off = max(abs(cx - m["seat"][0]), abs(cz - m["seat"][1]))
        if off > worst:
            worst, where = off, (m["mask"], round(float(cx - m["seat"][0]), 3), round(float(cz - m["seat"][1]), 3))
    return worst <= tol, "worst head-centre offset %.3f cell (mask, dx, dz = %s), tolerance %.2f" % (worst, where, tol)


CLAMP_BELOW = (0.03, 0.15)   # cell: how far the head's lowest opaque row hangs south of the seat (the clamp's front lip)


def head_clamp_straddles_pipe(scene, below=CLAMP_BELOW):
    """Exact placement: every head is centred across on its seat (bbox centre within half a bore in x) and its clamp
    straddles the pipe axis (lowest opaque row between below[0] and below[1] cell south of the seat): a head shifted
    north, south or sideways by a tenth of a cell fails."""
    heads, bad = _heads(scene), []
    if not heads:
        return False, "no head drawn"
    for m in heads:
        ys, xs = np.nonzero(_alpha(scene, m) > 40)
        if not len(xs):
            bad.append((m["mask"], "blank"))
            continue
        bx = (xs.min() + xs.max() + 1) / 2 / scene.P - m["seat"][0]
        hang = m["seat"][1] - (scene.h - (ys.max() + 1) / scene.P)
        if abs(bx) > BORE / 2 or not below[0] <= hang <= below[1]:
            bad.append((m["mask"], "dx %.3f" % bx, "hang %.3f" % hang))
    return not bad, ("off seat: %s (|dx| <= %.3f, hang %s)" % (bad[:4], BORE / 2, below)) if bad else "every clamp on its seat"


def head_squat(scene, max_ratio=1.0, min_bores=2.5):
    bad = []
    for m in _heads(scene)[:1]:          # one art per board: every station draws the same texture at the same size
        ys, xs = np.nonzero(_alpha(scene, m) > 40)
        if not len(xs):
            return False, "head at mask %s draws no opaque pixel" % m["mask"]
        w, h = (xs.max() - xs.min() + 1) / scene.P, (ys.max() - ys.min() + 1) / scene.P
        if h / w > max_ratio or w < min_bores * BORE:
            bad.append("%.3f wide x %.3f tall (h/w %.2f, needs <= %.2f; width needs >= %.3f)"
                       % (w, h, h / w, max_ratio, min_bores * BORE))
        else:
            return True, "%.3f wide x %.3f tall (h/w %.2f)" % (w, h, h / w)
    return False, "; ".join(bad) or "no head drawn"


def head_seat_on_pipe(scene):
    """Seat MATH on the drawn pipe: every head's seat (cell centre + RM_PipeSeatMath.Seat) lies on pipe alpha. It reads no
    head pixel: that the art's seat row lands on the seat is the drawOffset parity in selftest_fw_offline_art.py."""
    pipe = np.asarray(scene.render(only=lambda m: m.get("kind") == "pipe"))[..., 3]
    off = []
    for m in _heads(scene):
        x, y = scene.to_px(*m["seat"])
        r = max(1, round(BORE / 2 * scene.P))          # within half a bore: an end cell's pipe stops AT the seat
        win = pipe[max(0, round(y) - r):round(y) + r + 1, max(0, round(x) - r):round(x) + r + 1]
        if not (win >= 128).any():
            off.append(m["mask"])
    return not off, "seat off the drawn pipe at masks %s" % off if off else "every seat on drawn pipe"


SPRINKLER_CHECKS = (head_centroid_on_axis, head_clamp_straddles_pipe, head_squat, head_seat_on_pipe)


# ---- portable ladder (LADDER_PORTABLE_REDRAW_NORTH_FROM_GROUND) ------------------------------------------------------
# Owner 2026-10-24: "the one laying on its side looks really good" / the installed north "looks much less suitable";
# "yes I'd like to see the ground portable ladder used". On v5's south: "only small nubs sticking up".
# Inputs are RGBA images; the installed rig (RM_LadderPortable, 384 px at drawSize 1.5) and the ground sprite
# (RM_LadderPortableFlat, 256 px at drawSize 1) are both 256 px per cell.
LADDER_PX_PER_CELL = 256
LADDER_SOLID = 128           # alpha: opaque wood, not the soft contact shadow


def _ladder_geom(im):
    """(bbox x0, y0, x1, y1, mean rung pitch px) of an UPRIGHT ladder: rungs = opaque runs down its centre column."""
    a = np.asarray(im.convert("RGBA"))[..., 3] >= LADDER_SOLID
    ys, xs = np.nonzero(a)
    if not len(xs):
        return None
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    col = a[:, (x0 + x1) // 2]
    starts = [i for i in range(1, len(col)) if col[i] and not col[i - 1]]
    pitch = float(np.mean(np.diff(starts))) if len(starts) >= 2 else None
    return int(x0), int(y0), int(x1), int(y1), pitch


def ladder_north_not_compressed(north, flat_upright, keep=0.92, min_cells=0.85, rim_row=128, poke=(30, 90),
                                foot=(240, 330), centre_tol=8):
    """The installed north keeps the ground ladder's proportions: length/width and rung pitch/stringer span each
    within keep..1/keep x the ground sprite's (turned upright), it is at least min_cells long, and it stands where the rig shows a
    ladder on the far wall: its top pokes poke[0]..poke[1] px past the far rim (canvas row rim_row) and its foot rests in
    rows foot[0]..foot[1] (the face; a full face's foot is row 256), its wood centred on the canvas within centre_tol px.
    Two-sided: the ratios must lie within [keep, 1/keep] x the ground's, so a ladder squeezed across (or along) fails."""
    g, f = _ladder_geom(north), _ladder_geom(flat_upright)
    if g is None:
        return False, "north is blank"
    if g[4] is None or f[4] is None:
        return False, "fewer than two rungs found down the centre column (north %s, ground %s)" % (g[4], f[4])
    asp = lambda q: (q[3] - q[1] + 1) / (q[2] - q[0] + 1)
    rung = lambda q: q[4] / (q[2] - q[0] + 1)
    length = (g[3] - g[1] + 1) / LADDER_PX_PER_CELL
    off = (g[0] + g[2] + 1) / 2 - np.asarray(north).shape[1] / 2
    placed = poke[0] <= rim_row - g[1] <= poke[1] and foot[0] <= g[3] + 1 <= foot[1] and abs(off) <= centre_tol
    near = lambda a, b: keep * b <= a <= b / keep
    ok = near(asp(g), asp(f)) and near(rung(g), rung(f)) and length >= min_cells and placed
    return ok, "aspect %.2f vs ground %.2f, rung pitch/span %.2f vs %.2f, length %.2f cell, top row %d foot row %d, centre %+.0f px" % (
        asp(g), asp(f), rung(g), rung(f), length, g[1], g[3] + 1, off)


def ladder_south_footprint(south, rim_row=256, max_cells2=0.035, max_h_cells=0.12, rim_tol=8, min_nubs=2, centre_tol=8):
    """The south (seen from the near rim) is small nubs: >= min_nubs separate opaque column runs at least 3 px wide,
    opaque area <= max_cells2, height <= max_h_cells, standing on the rim, the pair centred within centre_tol px."""
    a = np.asarray(south.convert("RGBA"))[..., 3] >= LADDER_SOLID
    ys, xs = np.nonzero(a)
    if not len(xs):
        return False, "south is blank"
    cols = np.concatenate(([False], a.any(0), [False]))
    edges = np.flatnonzero(cols[1:] != cols[:-1]).reshape(-1, 2)
    nubs = int(np.sum(edges[:, 1] - edges[:, 0] >= 3))
    off = (xs.min() + xs.max() + 1) / 2 - a.shape[1] / 2
    area = a.sum() / LADDER_PX_PER_CELL ** 2
    h = (ys.max() - ys.min() + 1) / LADDER_PX_PER_CELL
    ok = (nubs >= min_nubs and area <= max_cells2 and h <= max_h_cells and abs(int(ys.max()) + 1 - rim_row) <= rim_tol
          and abs(off) <= centre_tol)
    return ok, "%d nubs, area %.3f cell2, height %.3f cell, foot row %d (rim %d), centre %+.0f px" % (
        nubs, area, h, ys.max() + 1, rim_row, off)
