#!/usr/bin/env python3
"""selftest_pipe_atlas_cell_geometry.py -- PIPE_ATLAS_REBUILD_OTHER_LOOKS_KINK: every installed universal-pipe atlas is
drawn on the cell vanilla Graphic_Linked shows (the inner 3/4 of each 4x4 tile, P = tile/8 of padding all round).

  G1 seams: art_source/pipe/check_pipe_atlas.py finds 0 failures (one crossing span per axis; each linked side's
     padding is exactly the boundary line of every neighbour that links back)
  G2 no elbow kink: on each elbow (masks 3, 6, 9, 12), over the last 8 px inside each linked edge, the bore's centre
     stays within 1 px of the straights' bore centre (an arc still curving at the edge drifts off it)
  G3 nothing in the padding but the pipe's continuation: every visible padding pixel lies in a linked side's bore
     strip (a coupling, cap or elbow drawn for a 176 px cell spills outside it)

Each truth is first shown able to fail on the pre-fix atlases (git blobs of PRE_FIX, the compose.py geometry), then run
on every installed look. Exit 0 when all hold; 1 lists every violation.
    python3 src/RimMandrake/FlowWorks/Tools/selftest_pipe_atlas_cell_geometry.py
"""
import contextlib
import io
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
REL = "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Pipe/%s/UniversalPipe_Atlas.png"
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")
FIXED = ("Industrial", "Modern", "Futuristic")
PRE_FIX = "3f9bb31156"          # the last commit with the compose.py (176 px cell) geometry on those three
N, E, S, W = 1, 2, 4, 8
OPAQUE = 128

sys.path.insert(0, str(ROOT / "src/RimMandrake/FlowWorks/art_source/pipe"))
import check_pipe_atlas  # noqa: E402


def tile(a, m):
    T = a.shape[1] // 4
    x, y = m % 4, m // 4
    return a[(3 - y) * T:(4 - y) * T, x * T:(x + 1) * T]


def seams(png, look):
    """G1, through check_pipe_atlas (its report captured)."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = check_pipe_atlas.main(png)
    return [] if rc == 0 else ["G1 %s: %s" % (look, out.getvalue().splitlines()[0].split(": ", 1)[-1])]


def bore_centre(a):
    """Centre (in cell px) of the opaque run across the E-W straight, the reference every elbow arm must hold."""
    T = a.shape[1] // 4
    P = T // 8
    col = tile(a, E | W)[P:T - P, T // 2, 3] > OPAQUE
    ys = np.nonzero(col)[0]
    return (ys[0] + ys[-1]) / 2.0


def kinks(a, look):
    T = a.shape[1] // 4
    P, C = T // 8, T - T // 4
    ref = bore_centre(a)
    bad = []
    for m in (N | E, E | S, S | W, W | N):
        cell = tile(a, m)[P:P + C, P:P + C, 3] > OPAQUE
        for d in (N, E, S, W):
            if not m & d:
                continue
            for k in range(8):
                line = {N: cell[k, :], S: cell[C - 1 - k, :], W: cell[:, k], E: cell[:, C - 1 - k]}[d]
                idx = np.nonzero(line)[0]
                c = (idx[0] + idx[-1]) / 2.0 if idx.size else float("nan")
                if not abs(c - ref) <= 1.0:
                    bad.append("G2 %s elbow %d: %d px inside its %s edge the bore centre is %.1f, the straights' %.1f"
                               % (look, m, k, {N: "N", E: "E", S: "S", W: "W"}[d], c, ref))
                    break
    return bad


def padding(a, look):
    T = a.shape[1] // 4
    P, C = T // 8, T - T // 4
    col = tile(a, E | W)[P:P + C, T // 2, 3] > OPAQUE     # the bore strip: the straight's own span, +1 px of antialias
    ys = np.nonzero(col)[0]
    b0, b1 = P + ys[0] - 1, P + ys[-1] + 2
    bad = []
    for m in range(16):
        al = tile(a, m)[..., 3] > 0
        allowed = np.zeros((T, T), bool)
        allowed[P:P + C, P:P + C] = True
        if m & N: allowed[:P, b0:b1] = True
        if m & S: allowed[P + C:, b0:b1] = True
        if m & W: allowed[b0:b1, :P] = True
        if m & E: allowed[b0:b1, P + C:] = True
        stray = int((al & ~allowed).sum())
        if stray:
            bad.append("G3 %s mask %d: %d visible padding px outside the linked bore strips" % (look, m, stray))
    return bad


def truths(png, look):
    a = np.asarray(Image.open(png).convert("RGBA"))
    return seams(png, look) + kinks(a, look) + padding(a, look)


def probes():
    fails = []
    for look in FIXED:
        blob = subprocess.run(["git", "show", "%s:%s" % (PRE_FIX, REL % look)], cwd=ROOT, capture_output=True)
        if blob.returncode:
            fails.append("probe: cannot read the pre-fix %s atlas at %s (%s)" % (look, PRE_FIX, blob.stderr.decode().strip()))
            continue
        bad = truths(io.BytesIO(blob.stdout), look)
        for g in ("G1", "G2", "G3"):
            if not any(b.startswith(g) for b in bad):
                fails.append("probe: %s does not fail on the pre-fix %s atlas" % (g, look))
    return fails


def main():
    fails = probes()
    if fails:
        print("\n".join(fails))
        return 1
    print("probes: G1, G2 and G3 each fail on the pre-fix Industrial, Modern and Futuristic atlases")
    bad = []
    for look in LOOKS:
        bad += truths(str(ROOT / (REL % look)), look)
    for g in ("G1", "G2", "G3"):
        mine = [b for b in bad if b.startswith(g)]
        print("%s: %s" % (g, "holds on %d looks" % len(LOOKS) if not mine else "%d violation(s)" % len(mine)))
    for b in bad:
        print("  " + b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
