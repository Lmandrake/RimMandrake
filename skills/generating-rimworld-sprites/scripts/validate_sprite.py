#!/usr/bin/env python3
"""validate_sprite.py — refuse RimWorld art that would waste a game load.

Every check here is decidable offline in milliseconds. A cold load costs
~23-30 minutes, so anything computable must be computed first.

Checks are graded. REJECT means the asset is not shippable. WARN means it is
suspicious and a human should look; `--strict` promotes warnings to rejections.

    python validate_sprite.py --reference orig.png --describe
    python validate_sprite.py --reference orig.png --candidate new.png
    python validate_sprite.py --reference orig.png --candidate new.png --strict

Exit codes: 0 pass, 1 not shippable, 2 unusable input.
"""

from __future__ import annotations

import argparse
import hashlib
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]
                       / "generating-images" / "scripts"))
import pnglib  # noqa: E402

REJECT, WARN = "REJECT", "WARN"

# --- thresholds, each with the observation that set it ------------------------

# Pixels at or above this are "visible" for rendering purposes.
ALPHA_VISIBLE = 8

# ...but geometry is measured here. A near-invisible fringe still counts as
# subject to a naive bbox, and on the first real smelter run ~1,900 pixels at
# alpha 8-31 inflated the measured box by 20% and silently produced a sprite
# 20% undersized. Measuring above the fringe is what makes geometry trustworthy.
ALPHA_SOLID = 32

# A clean cutout is bimodal - mostly clear, mostly solid, with a thin
# antialiasing band. A fat middle means the key thresholds were too wide and
# the art will render semi-transparent. Measured at 36% on the run that failed;
# a correct cut of the same image measured 0.02%.
MIDTONE_ALPHA_LO, MIDTONE_ALPHA_HI = 32, 224
MIDTONE_MAX_FRACTION = 0.08

# Faint pixels are the specific defect above. They are invisible on screen, so
# only a count catches them.
FRINGE_ALPHA_LO, FRINGE_ALPHA_HI = 1, 31
# Calibrated against the real defect, not guessed: the sprite that came out 20%
# undersized carried 0.12% fringe, and a correct cut of the same image carried
# 0.01%. A threshold of 0.5% - the first value tried - sat comfortably ABOVE the
# bug and would never have fired. Sits between the two measurements instead.
FRINGE_MAX_FRACTION = 0.0005

# How far faint pixels may reach past the solid silhouette before it is a
# defect rather than soft art. Anything beyond this inflates a naive bounding
# box measurably; the undersizing bug reached far past the machine, while
# legitimate smoke on the kludged smelter stayed inside it.
FRINGE_REACH_TOLERANCE = 0.02

# Linear extent, checked separately from area. THIS is the check that would
# have caught the undersizing: a wreck legitimately loses area (material is
# removed) but it must still span its footprint. Area tolerance therefore has
# to stay loose while span stays tight.
SPAN_TOLERANCE = 0.06

# Where the subject sits inside the canvas. RimWorld draws the texture against
# the def's drawSize, so a shifted subject sits off its tiles.
ORIGIN_TOLERANCE = 0.04

# Area may drop a long way for a wreck, but should not balloon.
COVERAGE_MIN_RATIO = 0.25
COVERAGE_MAX_RATIO = 1.15

# Subject aspect should survive any legitimate edit; a change here means the
# art was squashed rather than redrawn.
ASPECT_TOLERANCE = 0.06

# Below this the image is genuinely empty - no subject at all, as in the
# Cerean mane that ships with alpha max 0.
#
# ⚠️ This is deliberately near-zero rather than a "looks too sparse" floor.
# AGENT WORLD measured a healthy Facial Animation brow at ~0.15% coverage while
# auditing 46,508 live textures, so any absolute floor in the 0.5% range
# rejects correct art. Sparseness relative to the REFERENCE is what carries
# meaning, and COVERAGE_MIN_RATIO already tests that. A fixed floor cannot
# express "sparse but correct for this kind of asset".
EMPTY_COVERAGE = 0.0001

# Corners of a cut-out sprite must be clear.
CORNER_MAX_ALPHA = 8

# Residual key colour on the antialiased rim. Compares the mean colour of
# partial-alpha pixels against fully-opaque ones; a channel that jumps only at
# the edge is spill, not art.
SPILL_CHANNEL_DELTA = 24.0

# Detached fragments. Generation leaves stray blobs; a real sprite is one mass
# (RimWorld art can have separate parts, so this warns rather than rejects).
FRAGMENT_MAX_FRACTION = 0.02

# Flood fill is O(pixels) with a Python stack; above this we skip it rather
# than stall a pipeline. Conformed sprites are far below it.
FRAGMENT_PIXEL_BUDGET = 1_200_000


def measure(path: Path) -> dict:
    """One pass over the image; every later check reads this."""
    w, h, px = pnglib.read_png(str(path))
    n = w * h

    hist = [0] * 256
    vis = solid = 0
    min_x, min_y, max_x, max_y = w, h, -1, -1
    vmin_x, vmin_y, vmax_x, vmax_y = w, h, -1, -1
    sum_x = sum_y = 0
    opaque_rgb = [0, 0, 0]
    opaque_n = 0
    edge_rgb = [0, 0, 0]
    edge_n = 0
    touches = set()

    for y in range(h):
        for x in range(w):
            i = (y * w + x) * 4
            a = px[i + 3]
            hist[a] += 1
            if a >= ALPHA_VISIBLE:
                vis += 1
                if x < vmin_x: vmin_x = x
                if x > vmax_x: vmax_x = x
                if y < vmin_y: vmin_y = y
                if y > vmax_y: vmax_y = y
            if a < ALPHA_SOLID:
                continue
            solid += 1
            sum_x += x
            sum_y += y
            if x < min_x: min_x = x
            if x > max_x: max_x = x
            if y < min_y: min_y = y
            if y > max_y: max_y = y
            if x == 0: touches.add("left")
            if x == w - 1: touches.add("right")
            if y == 0: touches.add("top")
            if y == h - 1: touches.add("bottom")
            if a == 255:
                opaque_n += 1
                for c in range(3):
                    opaque_rgb[c] += px[i + c]
            elif a <= MIDTONE_ALPHA_HI:
                edge_n += 1
                for c in range(3):
                    edge_rgb[c] += px[i + c]

    has_alpha = sum(hist[:255]) > 0
    corners = [px[((cy * w) + cx) * 4 + 3]
               for cx, cy in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]

    return {
        "path": path, "w": w, "h": h, "px": px, "n": n,
        "hist": hist, "has_alpha": has_alpha,
        "visible": vis, "solid": solid,
        "coverage": solid / n if n else 0.0,
        "bbox": (min_x, min_y, max_x, max_y) if solid else None,
        "vis_bbox": (vmin_x, vmin_y, vmax_x, vmax_y) if vis else None,
        "span_w": (max_x - min_x + 1) if solid else 0,
        "span_h": (max_y - min_y + 1) if solid else 0,
        "centroid": (sum_x / solid, sum_y / solid) if solid else None,
        "corners": corners,
        "touches": touches,
        "mean_opaque": tuple(c / opaque_n for c in opaque_rgb) if opaque_n else None,
        "mean_edge": tuple(c / edge_n for c in edge_rgb) if edge_n else None,
        "fringe": sum(hist[FRINGE_ALPHA_LO:FRINGE_ALPHA_HI + 1]),
        "midtone": sum(hist[MIDTONE_ALPHA_LO:MIDTONE_ALPHA_HI + 1]),
        # Hash the PIXELS, not the file. Re-encoding identical pixels
        # yields different file bytes, which let an unchanged image pass.
        "sha": hashlib.sha256(bytes(px)).hexdigest()[:16],
    }


def fragment_fraction(s: dict) -> float | None:
    """Fraction of solid pixels NOT in the largest connected component."""
    if s["n"] > FRAGMENT_PIXEL_BUDGET or not s["solid"]:
        return None
    w, h, px = s["w"], s["h"], s["px"]
    seen = bytearray(w * h)
    biggest = 0
    total = 0
    for start in range(w * h):
        if seen[start] or px[start * 4 + 3] < ALPHA_SOLID:
            continue
        stack = [start]
        seen[start] = 1
        size = 0
        while stack:
            p = stack.pop()
            size += 1
            py, pxx = divmod(p, w)
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = py + dy, pxx + dx
                if 0 <= ny < h and 0 <= nx < w:
                    q = ny * w + nx
                    if not seen[q] and px[q * 4 + 3] >= ALPHA_SOLID:
                        seen[q] = 1
                        stack.append(q)
        total += size
        biggest = max(biggest, size)
    return (total - biggest) / total if total else 0.0


def describe(s: dict) -> None:
    print(f"{s['path'].name}")
    print(f"  canvas    {s['w']}x{s['h']}   aspect {s['w']/s['h']:.3f}")
    print(f"  alpha     {'yes' if s['has_alpha'] else 'NO ALPHA CHANNEL'}")
    print(f"  coverage  {s['coverage']:.1%}   solid px {s['solid']:,}")
    if s["bbox"]:
        print(f"  subject   {s['span_w']}x{s['span_h']} at "
              f"({s['bbox'][0]},{s['bbox'][1]})  aspect "
              f"{s['span_w']/max(s['span_h'],1):.3f}")
        print(f"  centroid  ({s['centroid'][0]:.0f},{s['centroid'][1]:.0f})")
    print(f"  alpha mix clear {s['hist'][0]/s['n']:.2%} | "
          f"fringe {s['fringe']/s['n']:.2%} | "
          f"mid {s['midtone']/s['n']:.2%} | solid {s['hist'][255]/s['n']:.2%}")
    print(f"  corners   {s['corners']}")
    if s["touches"]:
        print(f"  touches   canvas edge: {', '.join(sorted(s['touches']))}")
    print(f"  sha256    {s['sha']}")


def check(ref: dict, cand: dict) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []

    def add(level, msg):
        out.append((level, msg))

    # ⚠️ Refuse to judge against a degenerate reference rather than judging
    # badly. Every geometric and coverage test here is a RATIO against the
    # reference, so an empty one either divides by zero or accepts anything.
    # This is not hypothetical: AGENT WORLD's full-stack sweep found 355 fully
    # empty textures among 46,508 live files, and only 13 were bugs - the rest
    # are legitimate idioms (NullImage, blank droid heads, _north eye variants).
    # A comparison channel that cannot see the property being tested must error,
    # not answer confidently.
    if ref["bbox"] is None or ref["coverage"] <= 0:
        add(REJECT, "the REFERENCE is empty - it has no visible subject. Every "
                    "check here is a ratio against it, so nothing can be "
                    "judged. Point --reference at a healthy sibling facing.")
        return out

    # --- canvas -------------------------------------------------------------
    if (cand["w"], cand["h"]) != (ref["w"], ref["h"]):
        add(REJECT, f"canvas is {cand['w']}x{cand['h']}, reference is "
                    f"{ref['w']}x{ref['h']}. RimWorld draws against the def's "
                    f"drawSize; a mismatch shifts the art off its tiles.")

    # --- alpha health -------------------------------------------------------
    if not cand["has_alpha"]:
        add(REJECT, "no alpha channel - the background will render as an "
                    "opaque block.")

    hot = [i for i, a in enumerate(cand["corners"]) if a > CORNER_MAX_ALPHA]
    if hot:
        add(REJECT, f"{len(hot)} of 4 corners are opaque - the key was not "
                    f"fully removed, or the background was not flat.")

    fringe_frac = cand["fringe"] / cand["n"]
    if cand["bbox"] and cand["vis_bbox"]:
        # The harm a fringe does is inflating a naive measurement, so measure
        # THAT rather than counting faint pixels. Deliberately soft art - smoke,
        # glow, an antialiased rim - is faint and lives INSIDE the silhouette;
        # key residue reaches past it. Counting alone cannot tell them apart,
        # and rejected legitimate smoke on two facings before this was fixed.
        reach = max(
            (cand["bbox"][0] - cand["vis_bbox"][0]) / cand["w"],
            (cand["bbox"][1] - cand["vis_bbox"][1]) / cand["h"],
            (cand["vis_bbox"][2] - cand["bbox"][2]) / cand["w"],
            (cand["vis_bbox"][3] - cand["bbox"][3]) / cand["h"],
        )
        if reach > FRINGE_REACH_TOLERANCE:
            add(REJECT, f"faint pixels (alpha 1-31) reach {reach:.1%} of canvas "
                        f"BEYOND the solid silhouette. They are invisible on "
                        f"screen but count as subject, so they inflate every "
                        f"naive measurement. Raise the chroma key's lower "
                        f"threshold.")
        elif fringe_frac > FRINGE_MAX_FRACTION:
            add(WARN, f"{fringe_frac:.2%} of pixels are faint (alpha 1-31) but "
                      f"stay within the silhouette - consistent with soft art "
                      f"such as smoke or glow. Confirm it is intentional.")

    mid_frac = cand["midtone"] / cand["n"]
    if mid_frac > MIDTONE_MAX_FRACTION:
        add(REJECT, f"{mid_frac:.1%} of pixels are semi-transparent "
                    f"(alpha {MIDTONE_ALPHA_LO}-{MIDTONE_ALPHA_HI}). A clean "
                    f"cutout is bimodal; this will render washed out. Lower "
                    f"the chroma key's upper threshold.")

    # --- residual key spill -------------------------------------------------
    if cand["mean_edge"] and cand["mean_opaque"]:
        deltas = [cand["mean_edge"][c] - cand["mean_opaque"][c] for c in range(3)]
        worst = max(range(3), key=lambda c: deltas[c])
        if deltas[worst] > SPILL_CHANNEL_DELTA:
            add(WARN, f"the antialiased rim is {deltas[worst]:.0f}/255 more "
                      f"{'RGB'[worst]} than the body - residual key spill. "
                      f"Re-cut with despill, or --edge-contract.")

    # --- content ------------------------------------------------------------
    if cand["coverage"] < EMPTY_COVERAGE:
        add(REJECT, f"effectively empty ({cand['coverage']:.3%} solid) - no "
                    f"subject at all.")

    if cand["sha"] == ref["sha"]:
        add(REJECT, "byte-identical to the reference - nothing changed.")

    if cand["touches"] and not ref["touches"]:
        add(WARN, f"subject touches the canvas edge ({', '.join(sorted(cand['touches']))}) "
                  f"where the reference does not - the art may be clipped.")

    # --- geometry against the reference -------------------------------------
    if ref["bbox"] and cand["bbox"]:
        # Linear span. The check that catches undersizing, which area misses
        # because a wreck legitimately loses area but not reach.
        for label, c, r, canvas in (("width", cand["span_w"], ref["span_w"], ref["w"]),
                                    ("height", cand["span_h"], ref["span_h"], ref["h"])):
            drift = (c - r) / r
            if abs(drift) > SPAN_TOLERANCE:
                add(REJECT, f"subject {label} is {c}px against the reference's "
                            f"{r}px ({drift:+.0%}). A damaged variant may lose "
                            f"area but must still span its footprint.")
            over = (c - r) / canvas
            if over > 0.02:
                add(REJECT, f"subject {label} exceeds the reference by "
                            f"{over:.1%} of canvas - art outside the footprint "
                            f"overlaps neighbouring buildings in game.")

        ref_aspect = ref["span_w"] / max(ref["span_h"], 1)
        cand_aspect = cand["span_w"] / max(cand["span_h"], 1)
        if abs(cand_aspect - ref_aspect) / ref_aspect > ASPECT_TOLERANCE:
            add(REJECT, f"subject aspect {cand_aspect:.3f} against the "
                        f"reference's {ref_aspect:.3f} - the art was squashed, "
                        f"not redrawn.")

        for label, ci, ri, canvas in (("x", cand["bbox"][0], ref["bbox"][0], ref["w"]),
                                      ("y", cand["bbox"][1], ref["bbox"][1], ref["h"])):
            if abs(ci - ri) / canvas > ORIGIN_TOLERANCE:
                add(REJECT, f"subject origin {label}={ci} against the "
                            f"reference's {ri} - the subject sits in a "
                            f"different place on the canvas.")

        if ref["coverage"] > 0:
            ratio = cand["coverage"] / ref["coverage"]
            if ratio < COVERAGE_MIN_RATIO:
                add(REJECT, f"covers {ratio:.0%} of the reference's area - too "
                            f"much of the subject was removed or keyed away.")
            if ratio > COVERAGE_MAX_RATIO:
                add(WARN, f"covers {ratio:.0%} of the reference's area - the "
                          f"subject gained material.")

    # --- fragments ----------------------------------------------------------
    frag = fragment_fraction(cand)
    if frag is not None and frag > FRAGMENT_MAX_FRACTION:
        add(WARN, f"{frag:.1%} of solid pixels are in detached fragments "
                  f"rather than the main mass - stray blobs from generation, "
                  f"or intentionally separate parts.")

    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--reference", required=True)
    ap.add_argument("--candidate")
    ap.add_argument("--describe", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="treat warnings as rejections")
    args = ap.parse_args()

    ref_path = Path(args.reference)
    if not ref_path.is_file():
        print(f"ERROR no such reference: {ref_path}", file=sys.stderr)
        return 2
    ref = measure(ref_path)

    if args.describe or not args.candidate:
        describe(ref)
        if args.candidate and Path(args.candidate).is_file():
            print()
            describe(measure(Path(args.candidate)))
        return 0

    cand_path = Path(args.candidate)
    if not cand_path.is_file():
        print(f"ERROR no such candidate: {cand_path}", file=sys.stderr)
        return 2
    cand = measure(cand_path)

    describe(ref)
    print()
    describe(cand)
    print()

    findings = check(ref, cand)
    rejects = [m for lvl, m in findings if lvl == REJECT]
    warns = [m for lvl, m in findings if lvl == WARN]

    for m in rejects:
        print(f"REJECT {m}", file=sys.stderr)
    for m in warns:
        print(f"WARN   {m}", file=sys.stderr)

    if rejects or (warns and args.strict):
        n = len(rejects) + (len(warns) if args.strict else 0)
        print(f"\n{n} blocking problem(s) - do not deploy this.", file=sys.stderr)
        return 1

    print(f"PASS  shippable against this reference"
          f"{f' ({len(warns)} warning(s) - look at it)' if warns else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
