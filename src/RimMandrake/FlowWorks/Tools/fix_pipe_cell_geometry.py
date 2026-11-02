#!/usr/bin/env python3
"""PIPE_ATLAS_REBUILD_OTHER_LOOKS_KINK: put the Industrial, Modern and Futuristic pipe atlases on the cell geometry that
vanilla Graphic_Linked actually shows (Scrapper already is: art_source/pipe/build_pipe_atlas.py).

The 2026-10-22 composer (Transient/pile_2026-10-22/pipefit/compose.py) took the whole 176 px tile for the cell, but
SubMaterialFromAtlas shows only its inner 132 px (P = 22 px of padding all round). Two defects followed:
  * elbow kink: each elbow was bent on a radius about the TILE corner, so at the shown cell edge the arc is still
    curving and meets the straight neighbour at an angle;
  * couplings in the padding: the half-coupling meant for each joint sits in the never-shown padding, where it is
    sampled only by filtering/mipmaps, and the padding is not the neighbour's continuation (check_pipe_atlas.py).
(The third, the detached north/south caps, was fixed on 2026-10-26 by art_source/pipe/fix_ns_end_caps.py.)

This is a geometric correction, no new drawing (delegation_policy section 2, owner card 2026-10-26 18:46): every pixel
written is the look's own pipe cross-section, read from its own installed straight tiles.
  * every tile: the padding is cleared, then each linked side's padding carries the look's straight cross-section
    (the neighbour's continuation), and the side's boundary line inside the cell is set to that same cross-section;
  * the four elbows (masks 3, 6, 9, 12): the shown cell is redrawn as the look's cross-section swept on a radius of
    half a cell about the shown cell's corner, so each arm leaves the cell edge square-on at the bore of the straights.
Every other pixel of the shown cells (straights, tees, cross, caps, the Modern recolour) is left byte-identical
(written() is the exact set this script owns; Tools/selftest_fw_offline_art.py exempts the same set on Modern).

    fix_pipe_cell_geometry.py                    dry run: write candidates to the work dir and report the measures
    fix_pipe_cell_geometry.py --apply            install the three through art.py (old bytes archived, one-command revert)

Idempotent: the cross-section is a median over the straight's shown pixels inside its boundary lines, which this
script never writes, so a second run reproduces the same pixels.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
TEX = ROOT / "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Pipe"
ART = ROOT / "src/RimMandrake/Utils/art/art.py"
WORK = ROOT / "Transient" / "pipe_cell_geometry_work"     # inside the clone: art.py put refuses files outside it
LOOKS = ("Industrial", "Modern", "Futuristic")
N, E, S, W = 1, 2, 4, 8
CARD = ("To make the system more fire-and-forget, may I decide this class of art change without you from now on? "
        "→ Yes, delegate this class (Recommended)")
WHY = "delegated: art geometric correction (PIPE_ATLAS_REBUILD_OTHER_LOOKS_KINK; script:src/RimMandrake/FlowWorks/Tools/fix_pipe_cell_geometry.py)"


def geom(atlas):
    T = atlas.shape[1] // 4
    P = T // 8
    return T, P, T - 2 * P


def tile(atlas, m):
    """Tile of link mask m (vanilla Basic: rows of the 4x4 grid counted from the image bottom), as a view."""
    T = atlas.shape[1] // 4
    x, y = m % 4, m // 4
    return atlas[(3 - y) * T:(4 - y) * T, x * T:(x + 1) * T]


def profiles(atlas):
    """(top, hprof, vprof): the bore's first row/column inside the cell and the look's straight cross-sections, the
    per-row median of the E-W straight (mask 10) and per-column median of the N-S straight (mask 5) inside its boundary
    lines, each (W, 4)."""
    T, P, C = geom(atlas)
    h = tile(atlas, E | W)[P:P + C, P:P + C].astype(np.float64)
    v = tile(atlas, N | S)[P:P + C, P:P + C].astype(np.float64)
    rows = np.nonzero(h[:, :, 3].max(1) > 128)[0]
    cols = np.nonzero(v[:, :, 3].max(0) > 128)[0]
    if rows[0] != cols[0] or rows[-1] != cols[-1]:
        raise SystemExit("straights disagree on the bore: rows %s-%s vs cols %s-%s" % (rows[0], rows[-1], cols[0], cols[-1]))
    hp = np.median(h[rows[0]:rows[-1] + 1, 1:-1], axis=1)      # the boundary lines are left out: this script rewrites them
    vp = np.median(v[1:-1, cols[0]:cols[-1] + 1], axis=0)
    return int(rows[0]), hp, vp


def elbow(T, P, C, top, hp, vp, m):
    """The shown cell of elbow m: the cross-section swept about the shown cell's corner between its two linked sides."""
    Wd = hp.shape[0]
    R0 = top                                            # inner radius: the bore starts `top` px from the corner's edges
    cx = P + C if m & E else P                          # corner of the shown cell shared by the two linked sides
    cy = P if m & N else P + C
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float64) + 0.5
    dx, dy = xx - cx, yy - cy
    v = np.hypot(dx, dy) - R0                           # radial position across the bore, 0 at the inner wall
    f = np.arctan2(np.abs(dx), np.abs(dy)) / (np.pi / 2)   # 0 at the E-W end (straight below/above the corner), 1 at the N-S end
    vi = np.clip(np.floor(v).astype(int), 0, Wd - 1)
    hrow = vi if m & N else Wd - 1 - vi                 # E-W end: the inner wall faces the corner's row
    vcol = Wd - 1 - vi if m & E else vi                 # N-S end: the inner wall faces the corner's column
    w = np.clip((0.75 - f) / 0.5, 0, 1)[..., None]   # weight of the E-W cross-section
    rgb = hp[hrow, :3] * w + vp[vcol, :3] * (1 - w)
    cover = np.clip(np.minimum(v, Wd - v) + 0.5, 0, 1)
    inside = np.zeros((T, T), bool)
    inside[P:P + C, P:P + C] = True
    out = np.zeros((T, T, 4))
    out[..., :3] = rgb
    out[..., 3] = 255.0 * cover * inside
    return out


def written(T, P, C, m):
    """The pixels of tile m this correction owns: the padding ring, each linked side's boundary line, a whole elbow."""
    w = np.ones((T, T), bool)
    w[P:P + C, P:P + C] = m in (N | E, E | S, S | W, W | N)
    if m & N: w[P, :] = True
    if m & S: w[P + C - 1, :] = True
    if m & W: w[:, P] = True
    if m & E: w[:, P + C - 1] = True
    return w


def fixed(atlas):
    atlas = atlas.copy()
    T, P, C = geom(atlas)
    top, hp, vp = profiles(atlas)
    Wd = hp.shape[0]
    b0, b1 = P + top, P + top + Wd                      # bore span in tile px
    for m in range(16):
        t = tile(atlas, m)
        new = np.zeros((T, T, 4))
        if m in (N | E, E | S, S | W, W | N):
            new = elbow(T, P, C, top, hp, vp, m)
        # each linked side: the padding is the neighbour's continuation, and the boundary line is the same cross-section
        # (the whole boundary line is cleared first: an elbow's antialiased fringe must not reach the seam)
        if m & N: new[P, :] = 0; new[:P + 1, b0:b1] = vp[None]
        if m & S: new[P + C - 1, :] = 0; new[P + C - 1:, b0:b1] = vp[None]
        if m & W: new[:, P] = 0; new[b0:b1, :P + 1] = hp[:, None]
        if m & E: new[:, P + C - 1] = 0; new[b0:b1, P + C - 1:] = hp[:, None]
        new = np.clip(np.rint(new), 0, 255)
        new[new[..., 3] == 0] = 0                       # no colour under zero alpha (filtering samples it)
        w = written(T, P, C, m)
        t[w] = new[w].astype(np.uint8)                  # every other pixel (the shown straights, tees, caps) untouched
    return atlas


def main(argv):
    apply = "--apply" in argv
    WORK.mkdir(parents=True, exist_ok=True)
    for look in LOOKS:
        src = TEX / look / "UniversalPipe_Atlas.png"
        before = np.asarray(Image.open(src).convert("RGBA"))
        after = fixed(before)
        cand = WORK / ("%s_UniversalPipe_Atlas.png" % look)
        Image.fromarray(after, "RGBA").save(cand)
        changed = int((np.abs(after.astype(int) - before.astype(int)).max(2) > 0).sum())
        print("%s: %d px changed -> %s" % (look, changed, cand))
        if apply:
            if not changed:
                print("   already on the cell geometry; skipped")
                continue
            rel = "RimMandrake/FlowWorks/Pipe/%s/UniversalPipe_Atlas.png" % look
            r = subprocess.run([sys.executable, str(ART), "install", "FlowWorks", rel, "--file", str(cand),
                                "--by-card", CARD, "--why", WHY], cwd=ROOT, capture_output=True, text=True)
            print("  ", (r.stdout + r.stderr).strip().splitlines()[-1:] or "")
            if r.returncode:
                return r.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
