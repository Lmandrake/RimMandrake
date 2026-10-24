#!/usr/bin/env python3
"""Machine checks on fw_compositor renders: each owner-found art defect becomes a permanent check that reads the picture
(or the draw list behind it), proven to FAIL on the art he rejected and PASS on the fix (selftest_fw_offline_art.py runs
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
  head_squat             drawn no taller than wide, and at least 2.5 bore widths wide so it straddles any pipe
  head_seat_on_pipe      the seat point (cell centre + RM_PipeSeatMath) lands on drawn pipe (within half a bore)
Each returns (ok, detail).
"""
import math

import numpy as np

import fw_compositor as fc


def _popcount(m):
    return bin(m & 15).count("1")


def collar_on_riser(scene):
    im = np.asarray(scene.render(only=lambda m: m.get("kind") == "flange" and m.get("riser")))
    n = int((im[..., 3] > 32).sum())
    return n == 0, "%d flange pixels on riser pipes" % n


def end_cap_on_riser(scene):
    bad = sorted({(m["cell"], m["mask"]) for _, _, _, m in scene.draws
                  if m and m.get("kind") == "tile" and m.get("riser") and _popcount(m["mask"]) <= 1})
    return not bad, "dead-end tiles on riser cells: %s" % (bad or "none")


def _heading(seg, f):
    if seg[0] == "L":
        return math.degrees(math.atan2(seg[4] - seg[2], seg[3] - seg[1]))
    _, _, _, _, a0, sw = seg
    return a0 + sw * f + (90 if sw > 0 else -90)


def riser_kinks(scene, tol=2.0):
    worst, where = 0.0, None
    for cell, path in scene.risers:
        for a, b in zip(path, path[1:]):
            d = abs((_heading(b, 0) - _heading(a, 1) + 180) % 360 - 180)
            if d > worst:
                worst, where = d, cell
    return worst <= tol, "sharpest turn %.1f deg (cell %s)" % (worst, where)


def riser_gaps(scene, step=0.03, need=1.0):
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
    """Each riser strip, re-drawn on its own path with the scene's own orientation rule but a red-north/blue-south test
    tile: on the level run into the tank, red must be on the north side of the centreline and blue on the south."""
    probe = _probe_tile()
    bad, n = [], 0
    for _, _, _, m in scene.draws:
        if not m or m.get("kind") != "strip":
            continue
        cell, path = scene.risers[m["id"]]
        seg = path[-1]
        if seg[0] != "L" or abs(seg[4] - seg[2]) > 1e-9 or abs(seg[3] - seg[1]) < 0.1:
            continue
        t = fc.Scene(scene.w, scene.h, px=scene.P, ground=False)
        t.strip(probe, path, half_w=half_w, west=m.get("west"), meta={"kind": "probe"})
        im = np.asarray(t.render(only=lambda q: True), np.int32)
        x = (seg[1] + seg[3]) / 2
        nx, ny = map(int, t.to_px(x, seg[2] + half_w * 0.5))
        sx, sy = map(int, t.to_px(x, seg[2] - half_w * 0.5))
        north, south = im[ny, nx], im[sy, sx]
        n += 1
        if not (north[0] > north[2] and south[2] > south[0]):
            bad.append(cell)
    return n > 0 and not bad, "%d runs probed; north rim on the south at %s" % (n, bad or "none")


PIPE_JOIN_CHECKS = (collar_on_riser, end_cap_on_riser, riser_kinks, riser_gaps, riser_rims_north)


# ---- sprinkler head (scenes: fw_scenes_sprinkler.board) --------------------------------------------------------------
HEAD_TOL = 0.12      # cell: how far the head's alpha-weighted centre may sit from the drawn pipe centreline
BORE = 0.136         # cell: the universal pipe's bore width, every look (measured; fw_scenes_pipejoins.BORE_HALF)


def _heads(scene):
    return [m for _, _, _, m in scene.draws if m and m.get("kind") == "head"]


def _alpha(scene, meta):
    return np.asarray(scene.render(only=lambda m: m is meta))[..., 3].astype(float)


def head_centroid_on_axis(scene, tol=HEAD_TOL):
    worst, where = 0.0, None
    for m in _heads(scene):
        a = _alpha(scene, m)
        ys, xs = np.nonzero(a > 40)
        w = a[ys, xs]
        cx = (xs * w).sum() / w.sum() / scene.P
        cz = scene.h - (ys * w).sum() / w.sum() / scene.P
        off = max(abs(cx - m["seat"][0]), abs(cz - m["seat"][1]))
        if off > worst:
            worst, where = off, (m["mask"], round(cx - m["seat"][0], 3), round(cz - m["seat"][1], 3))
    return worst <= tol, "worst head-centre offset %.3f cell (mask, dx, dz = %s), tolerance %.2f" % (worst, where, tol)


def head_squat(scene, max_ratio=1.0, min_bores=2.5):
    bad = []
    for m in _heads(scene)[:1]:          # one art per board: every station draws the same texture at the same size
        ys, xs = np.nonzero(_alpha(scene, m) > 40)
        w, h = (xs.max() - xs.min() + 1) / scene.P, (ys.max() - ys.min() + 1) / scene.P
        if h / w > max_ratio or w < min_bores * BORE:
            bad.append("%.3f wide x %.3f tall (h/w %.2f, needs <= %.2f; width needs >= %.3f)"
                       % (w, h, h / w, max_ratio, min_bores * BORE))
        else:
            return True, "%.3f wide x %.3f tall (h/w %.2f)" % (w, h, h / w)
    return False, "; ".join(bad) or "no head drawn"


def head_seat_on_pipe(scene):
    pipe = np.asarray(scene.render(only=lambda m: m.get("kind") == "pipe"))[..., 3]
    off = []
    for m in _heads(scene):
        x, y = scene.to_px(*m["seat"])
        r = max(1, round(BORE / 2 * scene.P))          # within half a bore: an end cell's pipe stops AT the seat
        win = pipe[max(0, round(y) - r):round(y) + r + 1, max(0, round(x) - r):round(x) + r + 1]
        if not (win >= 128).any():
            off.append(m["mask"])
    return not off, "seat off the drawn pipe at masks %s" % off if off else "every seat on drawn pipe"


SPRINKLER_CHECKS = (head_centroid_on_axis, head_squat, head_seat_on_pipe)
