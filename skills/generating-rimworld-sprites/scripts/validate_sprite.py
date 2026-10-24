#!/usr/bin/env python3
"""validate_sprite.py — refuse RimWorld art that would waste a game load.

Every check here is decidable offline in milliseconds. A cold load costs
~23-30 minutes, so anything computable must be computed first.

Checks are graded. REJECT means the asset is not shippable. WARN means it is
suspicious and a human should look; `--strict` promotes warnings to rejections.

    python validate_sprite.py --reference orig.png --describe
    python validate_sprite.py --reference orig.png --candidate new.png
    python validate_sprite.py --reference orig.png --candidate new.png --strict
    python validate_sprite.py --reference tank.png --upright-cylinder        # camera check alone

`--upright-cylinder` adds the building-camera check for a vertical round thing (tank, silo, drum on end):
the top rim's minor/major axis must sit in the measured RimWorld band (references/building_camera_perspective.md).

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

REJECT, WARN, INFO = "REJECT", "WARN", "INFO"

# Building camera (TANK_TALL_BUILD_TWICE_THE_DRINK, 2026-10-14): the top rim of an upright cylinder, fitted on the
# silhouette, measured minor/major 0.55 (vanilla DeepDrill), 0.57 (vanilla BiofuelRefinery centre tank), 0.58-0.64
# (VFE Props tanks, VHGE gas tank), 0.48 (Spaceports fuel tank) => ~30-38 deg above horizontal, orthographic.
# The rejected 2026-10-14 tall tanks were side elevations whose domed top showed no rim at all. Band = measured
# range widened by ~0.02 each side; outside it the art reads as a different camera from every machine beside it.
CYL_RATIO_LO, CYL_RATIO_HI = 0.46, 0.66
# Clean rims fit at rms 0.3-0.5 px on all 7 references; lugs/valves crossing the rim push it past 4 (the rejected
# XTall: 17.6 px, a false 0.59). Above this the number is not a measurement. LIMIT: a domed head drawn in pure side
# elevation is ALSO an ellipse arc in silhouette and can pass - the check proves the rim's shape, never that a top
# FACE is painted; look at the picture.
CYL_FIT_RMS_MAX = 3.0

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
# A retired seat measured a healthy Facial Animation brow at ~0.15% coverage while
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


def rule_canvas_px(drawsize: float) -> int:
    """The def's rule canvas for a drawSize, from the pipeline's OWN size code (artpipe/common.py
    canvas_for_cells) — loaded by path, never re-derived here, so the two can never disagree."""
    import importlib.util
    src = Path(__file__).resolve().parents[3] / "src" / "RimMandrake" / "Utils" / "artpipe" / "common.py"
    spec = importlib.util.spec_from_file_location("artpipe_common_for_validator", src)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return int(mod.canvas_for_cells(float(drawsize)))


def rule_scale(ref: dict, cand: dict, rule_px: int | None) -> float | None:
    """ARTEVAL_VALIDATOR_FIX_REFUSES_HIRES_REDRAW: the factor by which a candidate's canvas legitimately differs from
    the reference's — only when the candidate is square on the def's rule canvas AND an exact integer multiple (or
    divisor) of the reference on BOTH axes by the same factor. None otherwise (the canvas check refuses as before)."""
    if not rule_px or (cand["w"], cand["h"]) != (rule_px, rule_px):
        return None
    for big, small in ((cand, ref), (ref, cand)):
        if big["w"] % small["w"] == 0 and big["h"] % small["h"] == 0:
            kw, kh = big["w"] // small["w"], big["h"] // small["h"]
            if kw == kh and kw >= 2:
                return float(kw) if big is cand else 1.0 / kw
    return None


def scaled_reference(ref: dict, f: float) -> dict:
    """The reference's geometry as it would sit on a canvas `f` times its size (coverage is a canvas fraction and
    does not change). Only the fields the geometry checks read are scaled; the pixels are not resampled."""
    r = dict(ref)
    r["w"], r["h"] = round(ref["w"] * f), round(ref["h"] * f)
    r["span_w"], r["span_h"] = round(ref["span_w"] * f), round(ref["span_h"] * f)
    if ref["bbox"]:
        r["bbox"] = tuple(round(v * f) for v in ref["bbox"])
    return r


def check(ref: dict, cand: dict, rule_px: int | None = None) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []

    def add(level, msg):
        out.append((level, msg))

    # ⚠️ Refuse to judge against a degenerate reference rather than judging
    # badly. Every geometric and coverage test here is a RATIO against the
    # reference, so an empty one either divides by zero or accepts anything.
    # This is not hypothetical: a retired seat's full-stack sweep found 355 fully
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
        f = rule_scale(ref, cand, rule_px)
        if f is None:
            add(REJECT, f"canvas is {cand['w']}x{cand['h']}, reference is "
                        f"{ref['w']}x{ref['h']}. RimWorld draws against the def's "
                        f"drawSize; a mismatch shifts the art off its tiles."
                        + (f" (the def's rule canvas is {rule_px}x{rule_px}; only an exact multiple of the "
                           f"reference ON that canvas is judged at scale)" if rule_px else ""))
        else:
            add(INFO, f"canvas {cand['w']}x{cand['h']} is the def's rule canvas and exactly {f:g}x the "
                      f"reference's {ref['w']}x{ref['h']} - geometry judged against the reference scaled "
                      f"to it (ARTEVAL_VALIDATOR_FIX_REFUSES_HIRES_REDRAW)")
            ref = scaled_reference(ref, f)

    # --- alpha health -------------------------------------------------------
    if not cand["has_alpha"]:
        add(REJECT, "no alpha channel - the background will render as an "
                    "opaque block.")

    hot = [i for i, a in enumerate(cand["corners"]) if a > CORNER_MAX_ALPHA]
    if hot:
        add(REJECT, f"{len(hot)} of 4 corners are opaque - the image was drawn "
                    f"with a background instead of a real alpha channel. Ask "
                    f"for transparency in the prompt and regenerate.")

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
                        f"naive measurement. Regenerate; native alpha carries "
                        f"a 1-31 fringe too, so this check still earns its "
                        f"place.")
        elif fringe_frac > FRINGE_MAX_FRACTION:
            add(WARN, f"{fringe_frac:.2%} of pixels are faint (alpha 1-31) but "
                      f"stay within the silhouette - consistent with soft art "
                      f"such as smoke or glow. Confirm it is intentional.")

    mid_frac = cand["midtone"] / cand["n"]
    if mid_frac > MIDTONE_MAX_FRACTION:
        add(REJECT, f"{mid_frac:.1%} of pixels are semi-transparent "
                    f"(alpha {MIDTONE_ALPHA_LO}-{MIDTONE_ALPHA_HI}). A clean "
                    f"cutout is bimodal; this will render washed out. "
                    f"Regenerate rather than post-processing it.")

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

    new_touches = cand["touches"] - ref["touches"]
    if new_touches:
        add(WARN, f"subject touches the canvas edge ({', '.join(sorted(new_touches))}) "
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
    if cand["n"] > FRAGMENT_PIXEL_BUDGET:
        add(INFO, f"fragment check skipped - canvas is {cand['n']:,} px, over the "
                  f"{FRAGMENT_PIXEL_BUDGET:,} px budget. Detached-blob defects on "
                  f"this asset would not be caught.")
    else:
        frag = fragment_fraction(cand)
        if frag is not None and frag > FRAGMENT_MAX_FRACTION:
            add(WARN, f"{frag:.1%} of solid pixels are in detached fragments "
                      f"rather than the main mass - stray blobs from generation, "
                      f"or intentionally separate parts.")

    return out


def cylinder_top_ratio(path: Path) -> tuple[float, float] | None:
    """Fit the TOP silhouette of an upright cylinder to an ellipse arc; return (minor/major, rms px) or None.
    Body edges are read at mid-height of the subject (fittings above or below do not widen them); each half is
    fitted on its own over 0.3 <= |u| <= 0.9 and the better half wins, so a pipe or wheel on one side is tolerated."""
    w, h, px = pnglib.read_png(str(path))
    solid = lambda x, y: px[(y * w + x) * 4 + 3] >= 128
    rows = [y for y in range(h) if any(solid(x, y) for x in range(0, w, 2))]
    if not rows:
        return None
    mid = (rows[0] + rows[-1]) // 2
    xs = [x for x in range(w) if solid(x, mid)]
    if len(xs) < 8:
        return None
    left, right = xs[0], xs[-1]
    a, cx = (right - left + 1) / 2, (left + right) / 2
    best = None
    for side in (-1, 1):
        us, ys = [], []
        for x in range(left, right + 1):
            u = (x - cx) / a
            if not (0.3 <= abs(u) <= 0.9) or u * side < 0:
                continue
            y = next((y for y in range(h) if solid(x, y)), None)
            if y is None:
                continue
            us.append(math.sqrt(1 - u * u)); ys.append(y)
        if len(us) < 6:
            continue
        mu, my = sum(us) / len(us), sum(ys) / len(ys)
        var = sum((p - mu) ** 2 for p in us)
        if var == 0:
            continue
        k = sum((p - mu) * (q - my) for p, q in zip(us, ys)) / var
        rms = math.sqrt(sum((q - (my + k * (p - mu))) ** 2 for p, q in zip(us, ys)) / len(us))
        if best is None or rms < best[1]:
            best = (abs(k) / a, rms)
    return best


def cylinder_finding(path: Path) -> tuple[str, str]:
    r = cylinder_top_ratio(path)
    if r is None:
        return WARN, "camera: no upright-cylinder silhouette to fit"
    ratio, rms = r
    deg = math.degrees(math.asin(min(1.0, ratio)))
    msg = (f"camera: top rim minor/major {ratio:.2f} (~{deg:.0f} deg above horizontal, fit rms {rms:.1f}px); "
           f"RimWorld buildings measure {CYL_RATIO_LO + 0.02:.2f}-{CYL_RATIO_HI - 0.02:.2f}")
    if rms > CYL_FIT_RMS_MAX:
        return WARN, msg + f" - fit unreliable (rms > {CYL_FIT_RMS_MAX:.0f}px: something crosses the rim); judge by eye"
    if CYL_RATIO_LO <= ratio <= CYL_RATIO_HI:
        return INFO, msg + " - camera ok"
    return WARN, msg + (" - drawn too side-on (a side elevation, no top face)" if ratio < CYL_RATIO_LO
                        else " - drawn too top-down")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--reference", required=True)
    ap.add_argument("--candidate")
    ap.add_argument("--describe", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="treat warnings as rejections")
    ap.add_argument("--upright-cylinder", action="store_true",
                    help="also check the building camera: top-rim ellipse of a vertical round subject")
    ap.add_argument("--drawsize", help="the def's drawSize (cells): a candidate on its rule canvas "
                                       "(artpipe canvas_for_cells) at an exact multiple of the reference is "
                                       "judged at scale instead of refused for canvas size")
    args = ap.parse_args()

    rule_px = None
    if args.drawsize is not None:
        try:
            ds = float(args.drawsize)
            if not ds > 0:
                raise ValueError("drawSize must be > 0")
            rule_px = rule_canvas_px(ds)
        except Exception as e:        # noqa: BLE001 - an unusable drawSize is unusable input (2), never a verdict (1)
            print(f"ERROR cannot derive the rule canvas from --drawsize {args.drawsize!r}: {e}", file=sys.stderr)
            return 2

    ref_path = Path(args.reference)
    if not ref_path.is_file():
        print(f"ERROR no such reference: {ref_path}", file=sys.stderr)
        return 2
    try:
        ref = measure(ref_path)
    except Exception as e:            # noqa: BLE001 - an unreadable PNG is unusable input (2), never a verdict (1)
        print(f"ERROR cannot read reference {ref_path}: {e}", file=sys.stderr)
        return 2

    if args.upright_cylinder and not args.candidate:
        lvl, msg = cylinder_finding(ref_path)
        print(f"{lvl:<6} {msg}")
        return 1 if lvl != INFO else 0

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
    try:
        cand = measure(cand_path)
    except Exception as e:            # noqa: BLE001 - same: exit 2, not a "not shippable" traceback
        print(f"ERROR cannot read candidate {cand_path}: {e}", file=sys.stderr)
        return 2

    describe(ref)
    print()
    describe(cand)
    print()

    findings = check(ref, cand, rule_px)
    if args.upright_cylinder:
        findings.append(cylinder_finding(cand_path))
    rejects = [m for lvl, m in findings if lvl == REJECT]
    warns = [m for lvl, m in findings if lvl == WARN]
    infos = [m for lvl, m in findings if lvl == INFO]

    for m in rejects:
        print(f"REJECT {m}", file=sys.stderr)
    for m in warns:
        print(f"WARN   {m}", file=sys.stderr)
    for m in infos:
        print(f"INFO   {m}", file=sys.stderr)

    if rejects or (warns and args.strict):
        n = len(rejects) + (len(warns) if args.strict else 0)
        print(f"\n{n} blocking problem(s) - do not deploy this.", file=sys.stderr)
        return 1

    print(f"PASS  shippable against this reference"
          f"{f' ({len(warns)} warning(s) - look at it)' if warns else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
