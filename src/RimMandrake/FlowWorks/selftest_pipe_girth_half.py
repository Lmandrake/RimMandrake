"""PIPE_GIRTH_TUNE_HALF_AS_THICK (owner walk 2026-10-21: "that pipe is crazy thick. Make the pipes half as thick"):
the ground pipe's girth is baked into each look's linked atlas (Graphic_Linked draws the PNG on a 1x1 cell quad; no C# mesh
width exists for the ground pipe), so the ratio is asserted on the PNGs here. The C# SelfTest cannot: the winbuild stage
copies no Textures folder; it asserts only the pole span width (PipePoleChecks, RM_PipePoleMath.SpanWidthCells).

Measured per look, on the displayed inner C x C of each atlas tile (vanilla Basic link format, see
art_source/pipe/build_pipe_atlas.py), alpha > 128:
  - girth: every link arm of every tile (straights, elbows, tees, cross, caps) crosses the cell edge 0.12-0.15 cell wide
    (was 0.30 before 8d5b94b0e1);
  - joints: the junction box on the cell diagonal of the tee/cross tiles is <= 0.27 cell (was 0.47-0.53);
  - end caps: the widest column of a one-arm tile is <= 0.30 cell (was 0.38-0.47);
  - Scrapper's straight-variant sheet (UniversalPipe_Straights) carries the same 0.12-0.15 girth.

  - end caps attach (PIPE_CAP_FIX_NORTH_END_FLOATS_FREE, live round 4 2026-10-26): every one-arm tile is one unbroken run
    from its linked edge through the cap (no empty cross-section), and the north/south caps are as wide as the east/west
    ones (the 2026-10-22 composer cropped the quarter-turned cap to the pipe's width and floated it 7-10 px clear). The
    looks in CAPS_OPEN print OPEN instead of FAIL while the fixed atlases wait on the owner's ruling (they are owner-KEPT).

Can-fail: --canfail measures the pre-8d5b94b0e1 atlases (read from git) and must FAIL every look; --canfail-caps measures
the atlases at CAPS_BEFORE_SHA and must FAIL the cap check on Industrial, Modern and Futuristic.

    python3 src/RimMandrake/FlowWorks/selftest_pipe_girth_half.py [--canfail | --canfail-caps]
"""
from __future__ import annotations

import io
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PIPE = os.path.join(HERE, "Textures", "RimMandrake", "FlowWorks", "Pipe")
REL = "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Pipe"
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")
BEFORE_SHA = "8d5b94b0e1^"  # the last commit with the 0.30-cell pipe
CAPS_BEFORE_SHA = "d95104ac0c"  # the last atlases with the floating north/south caps
CAPS_BAD_LOOKS = ("Industrial", "Modern", "Futuristic")
# The shipped atlases are owner-KEPT, so the fix (art_source/pipe/fix_ns_end_caps.py) waits on his ruling. Until then these
# looks report OPEN, provided the fix script's output passes the cap check; a look here whose shipped caps attach FAILs as
# stale, so the entry cannot outlive the fix.
CAPS_OPEN = ("Industrial", "Modern", "Futuristic")
GIRTH = (0.12, 0.15)
JOINT_MAX = 0.27
CAP_MAX = 0.30
N, E, S, W = 1, 2, 4, 8


def alpha(img_bytes_or_path):
    im = Image.open(io.BytesIO(img_bytes_or_path) if isinstance(img_bytes_or_path, bytes) else img_bytes_or_path)
    return np.asarray(im.convert("RGBA"))[..., 3] > 128


def tile(a, i):
    """Displayed inner C x C of sub-material i (rows counted from the image bottom)."""
    t = a.shape[0] // 4
    p = t // 8
    y0 = a.shape[0] - (i // 4 + 1) * t
    x0 = (i % 4) * t
    return a[y0 + p:y0 + t - p, x0 + p:x0 + t - p]


def measure(a):
    """(fails, summary) for one atlas alpha mask."""
    bad = []
    c = a.shape[0] // 4 - 2 * (a.shape[0] // 4 // 8)
    girths, joints, caps = [], [], []
    for i in range(1, 16):
        t = tile(a, i)
        # each arm crosses its cell edge; sample 3 px inside the edge
        for bit, line in ((N, t[3, :]), (S, t[-4, :]), (E, t[:, -4]), (W, t[:, 3])):
            if i & bit:
                g = line.sum() / c
                girths.append(g)
                if not GIRTH[0] <= g <= GIRTH[1]:
                    bad.append("tile %d arm %d: girth %.3f cell not in %.2f-%.2f" % (i, bit, g, GIRTH[0], GIRTH[1]))
        arms = bin(i).count("1")
        if arms >= 3:
            j = np.array([t[k, k] for k in range(c)]).sum() / c
            joints.append(j)
            if j > JOINT_MAX:
                bad.append("tile %d: joint %.3f cell > %.2f" % (i, j, JOINT_MAX))
        if arms == 1:
            # widest cross-section perpendicular to the one arm (N/S arm: a row; E/W arm: a column)
            cap = (t.sum(1).max() if i & (N | S) else t.sum(0).max()) / c
            caps.append(cap)
            if cap > CAP_MAX:
                bad.append("tile %d: end cap %.3f cell > %.2f" % (i, cap, CAP_MAX))
    summary = "girth %.3f-%.3f joint<=%.3f cap<=%.3f" % (min(girths), max(girths), max(joints), max(caps))
    return bad, summary


def cap_faults(a):
    """Cap attachment faults of one atlas alpha mask: a gap along a one-arm tile, or N/S caps narrower than E/W ones."""
    bad = []
    width = {}
    for i in (N, E, S, W):
        t = tile(a, i)
        along = t.sum(1) if i & (N | S) else t.sum(0)   # cross-section count per step along the arm
        occ = np.nonzero(along)[0]
        if not len(occ):
            bad.append("tile %d: empty, no arm or cap drawn" % i)
            continue
        gap = int((along[occ.min():occ.max() + 1] == 0).sum())
        if gap:
            bad.append("tile %d: cap floats free, %d empty cross-sections between arm and cap" % (i, gap))
        width[i] = int(along.max())
    if len(width) == 4 and min(width[N], width[S]) < max(width[E], width[W]) - 1:
        bad.append("north/south cap %d px narrower than east/west cap %d px" % (min(width[N], width[S]), max(width[E], width[W])))
    return bad


def fixed_alpha(look):
    """Alpha mask of fix_ns_end_caps.fixed() applied to the shipped atlas of `look`."""
    sys.path.insert(0, os.path.join(HERE, "art_source", "pipe"))
    import fix_ns_end_caps as F
    px = np.asarray(Image.open(os.path.join(PIPE, look, "UniversalPipe_Atlas.png")).convert("RGBA"))
    return F.fixed(px)[..., 3] > 128


def straights_girth(a):
    """Scrapper sheet (PipeStraightVariants.Uvs): Count columns x 2 rows of T x T tiles, row 0 (top) east-west, row 1
    north-south, the shown cell the inner C x C; girth across the band 3 px inside both cell edges."""
    t = a.shape[0] // 2
    p = t // 8
    c = t - 2 * p
    out = []
    for k in range(a.shape[1] // t):
        ew = a[p:t - p, k * t + p:(k + 1) * t - p]
        ns = a[t + p:2 * t - p, k * t + p:(k + 1) * t - p]
        out += [ew[:, 3].sum() / c, ew[:, -4].sum() / c, ns[3, :].sum() / c, ns[-4, :].sum() / c]
    return out


def git_blob(rel, sha=BEFORE_SHA):
    return subprocess.run(["git", "show", "%s:%s" % (sha, rel)], cwd=HERE, capture_output=True, check=True).stdout


def canfail_caps():
    missed = [look for look in CAPS_BAD_LOOKS
              if not cap_faults(alpha(git_blob("%s/%s/UniversalPipe_Atlas.png" % (REL, look), CAPS_BEFORE_SHA)))]
    if missed:
        print("FAIL can-fail caps: the floating caps at %s read clean on %s" % (CAPS_BEFORE_SHA, ", ".join(missed)))
        return 1
    print("PASS can-fail caps: the %s atlases fail the cap check on %s" % (CAPS_BEFORE_SHA, ", ".join(CAPS_BAD_LOOKS)))
    return 0


def main(argv):
    if "--canfail-caps" in argv:
        return canfail_caps()
    canfail = "--canfail" in argv
    failed = 0
    for look in LOOKS:
        if canfail:
            a = alpha(git_blob("%s/%s/UniversalPipe_Atlas.png" % (REL, look)))
        else:
            a = alpha(os.path.join(PIPE, look, "UniversalPipe_Atlas.png"))
        bad, summary = measure(a)
        if not canfail:
            cf = cap_faults(a)
            if look not in CAPS_OPEN:
                bad += cf
            elif not cf:
                bad.append("stale CAPS_OPEN: the shipped caps attach now; drop %s from CAPS_OPEN" % look)
            else:
                fix_bad = cap_faults(fixed_alpha(look))
                bad += ["fix_ns_end_caps output: " + b for b in fix_bad]
                if not fix_bad:
                    print("OPEN %s: %d cap fault(s) shipped; fix_ns_end_caps output passes, awaiting the owner's ruling "
                          "(PIPE_CAP_FIX_NORTH_END_FLOATS_FREE)" % (look, len(cf)))
        print("%s %s: %s" % ("FAIL" if bad else "PASS", look, summary))
        for b in bad[:4]:
            print("    " + b)
        failed += bool(bad)
    if not canfail:
        sheet = os.path.join(PIPE, "Scrapper", "UniversalPipe_Straights.png")
        gs = straights_girth(alpha(sheet))
        ok = bool(gs) and all(GIRTH[0] <= g <= GIRTH[1] for g in gs)
        span = "%.3f-%.3f" % (min(gs), max(gs)) if gs else "unmeasurable (no tiles)"
        print("%s Scrapper straights sheet: %d edge crossings, girth %s" % ("PASS" if ok else "FAIL", len(gs), span))
        failed += not ok
    if canfail:
        if failed == len(LOOKS):
            print("PASS can-fail: every pre-halving atlas fails")
            return 0
        print("FAIL can-fail: only %d of %d pre-halving atlases fail" % (failed, len(LOOKS)))
        return 1
    print("%s %d/%d" % ("PASS" if not failed else "FAIL", len(LOOKS) + 1 - failed, len(LOOKS) + 1))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
