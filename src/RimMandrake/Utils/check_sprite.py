#!/usr/bin/env python3
"""check_sprite.py — art intake validator, general to any mod in this repo.

WHY THIS EXISTS, AND WHY IT IS THIN
===================================
Queue item C8 asked for six checks: canvas size, real alpha, zero saturated
pixels, value distribution, bounding box, and south/north silhouette parity.
Three of them were ALREADY BUILT and better than the spec, in
`skills/generating-rimworld-sprites/scripts/validate_sprite.py`:

  * canvas size, taken from a REFERENCE asset rather than a constant
  * real alpha, plus corner residue, midtone smear, fringe reach, key spill
  * bounding box, as span / origin / aspect / coverage against the reference

So this file does not reimplement them. It imports that module, runs it, and
adds ONLY the three checks nobody had written:

  * saturated pixels   — measured at exactly ZERO on every shipping asset in
                         this repo (see THRESHOLDS), so any count is a signal
  * value distribution — catches a flat fill, a crushed image and a blown one
  * facing parity      — south vs north silhouette, which no single-file
                         validator can see because it needs two files at once

plus one defect `validate_sprite.py` structurally cannot catch: an image whose
alpha channel exists but contains NO fully transparent pixel. Its `has_alpha`
test is `any alpha < 255`, and
`src/RimMandrake/MissingArtFixes/Textures/Things/Apparel/ToolBelt/ToolBelt_west.png`
passes it while having zero clear pixels — every corner sits at alpha 3. That is
the "white box on the factory floor" failure the alpha check was written for.

🔴 THE CANVAS IS AN ARGUMENT, NEVER A CONSTANT
==============================================
`WreckedMachines/Source/check_sprite.py` hardcoded nothing but its own manifest,
and this one hardcodes nothing at all. Queue item C5 records why: three blast
door placeholders are 267x267 while the true canvas is 933x933. Art drawn to the
placeholder's size would validate as "same size as what I replaced" and render
tiny in game. So the expected canvas comes from `--reference` (an asset whose
size is known good) or from an explicit `--canvas WxH`, and if both are given
and disagree, this refuses to run rather than picking one.

USAGE
  # self-checks only, no reference needed
  check_sprite.py Textures/Things/Foo_south.png

  # a whole folder, with facing parity across any _south/_north pair in it
  check_sprite.py Textures/Things/Foo/

  # the real intake gate: compare against the asset being replaced
  check_sprite.py new_east.png --reference healthy_north.png

  # canvas asserted explicitly, when there is no reference asset to point at
  check_sprite.py new.png --canvas 933x933

  # numbers only, no verdict
  check_sprite.py Foo_south.png --describe

EXIT CODES
  0  shippable (warnings allowed unless --strict)
  1  at least one REJECT
  2  unusable input (missing file, unreadable PNG, contradictory arguments)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Locate the shared modules. Utils/ sits at src/RimMandrake/Utils, so the repo
# root is three levels up. Resolved from __file__ rather than the cwd, because
# this is called from mod Source/ folders and from refresh.py alike.
# --------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[2]
for _p in (_REPO / "skills" / "generating-rimworld-sprites" / "scripts",
           _REPO / "skills" / "generating-images" / "scripts"):
    if _p.is_dir() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

try:
    import validate_sprite as VS                     # noqa: E402
    import pnglib                                    # noqa: E402
    HAVE_VS = True
except Exception as _e:                              # pragma: no cover
    VS = None                                        # type: ignore
    pnglib = None                                    # type: ignore
    HAVE_VS = False
    _IMPORT_ERROR = _e

REJECT, WARN = "REJECT", "WARN"

# --------------------------------------------------------------------------
# THRESHOLDS — each one carries the measurement that set it.
# Measured 2026-08-13 over seven real files in this repo: the wrecked
# AutomatedSmelter south/north (512x640), AV_DogSled south/north (512x512),
# the Jawa ion blaster and bullet (256x256), and the known-broken ToolBelt_west.
# --------------------------------------------------------------------------

# A pixel counts toward geometry and colour only above this alpha; below it the
# pixel is invisible on screen and only distorts the statistics. Same value
# validate_sprite.py uses, deliberately, so the two agree on what "drawn" means.
ALPHA_SOLID = 32

# SATURATION. A pixel is "saturated" when it is bright AND almost pure hue.
# RimWorld's palette is muted; a fully saturated pixel is the signature of
# generated art that never got colour-graded. Measured count on all seven real
# files: ZERO, without exception. So the queue's "zero saturated pixels" is not
# an aspiration, it is the observed norm, and any count at all is worth saying.
SAT_MIN_VALUE = 200          # max(r,g,b) at or above this is "bright"
SAT_MIN_CHROMA = 0.90        # (max-min)/max at or above this is "pure hue"
SAT_WARN_FRACTION = 0.001    # 0.1% of drawn pixels
SAT_REJECT_FRACTION = 0.01   # 1% is no longer a stray pixel, it is the palette

# VALUE DISTRIBUTION. Distinct luminance levels among drawn pixels. Measured:
# 93-247 on real art, on assets as small as 256x256 and as sparse as 5,749
# drawn pixels. A flat fill or a solid-colour placeholder lands in single
# digits, so this separates them with two orders of magnitude to spare.
MIN_DISTINCT_LUMA = 8
# Crushed / blown. Measured darkest-16-levels share: 0.00-0.32. Lightest: 0.00
# -0.12. A threshold of 0.70 sits far above every healthy measurement and still
# fires on an image that is essentially one end of the range.
CRUSHED_FRACTION = 0.70
BLOWN_FRACTION = 0.70
# Mean luminance drift against a reference, in levels out of 255. Measured
# south-vs-north drift on real facing pairs: 0.4 and 0.7 levels.
#
# ⚠️ Set to 60, not 40. At 40 it fired on the wrecked AutomatedSmelter east and
# west against their restored sources, at -41 and -41 levels - and that drift is
# the POINT of a damaged tier, which is scorched and unlit. A threshold that
# rejects the intended edit is a threshold that gets switched off. 60 still
# catches a genuinely different palette while leaving deliberate damage alone.
MEAN_LUMA_DRIFT = 60.0

# FULLY TRANSPARENT PIXELS. The share of the canvas at alpha exactly 0.
# Measured on healthy art: 0.411, 0.418 (the dense smelter) and 0.894, 0.895
# (the sparse dog sled). On the known broken ToolBelt_west: 0.0000 exactly.
# Nothing at all sits between zero and the sparsest healthy asset.
CLEAR_MIN_FRACTION = 0.02

# FACING PARITY. A building's south and north views show the same footprint
# from opposite sides, so the drawn mass must span the same width. Measured
# south-vs-north span difference: smelter 2.1% wide / 0.0% tall, sled 0.0% wide
# / 0.9% tall. A 15% tolerance is seven times the worst real value.
PARITY_SPAN_TOLERANCE = 0.15
# Where the mass sits on the canvas, as a fraction of canvas. Measured origin
# difference: 2px of 512 (0.4%) and 1px of 512 (0.2%).
PARITY_ORIGIN_TOLERANCE = 0.05
# Area may genuinely differ - a machine's back has less detail than its front.
# Measured coverage ratios: 0.988 and 0.984. Kept loose on purpose.
PARITY_COVERAGE_LO, PARITY_COVERAGE_HI = 0.60, 1.66

_FACINGS = ("south", "north", "east", "west")


# --------------------------------------------------------------------------
# The measurements validate_sprite.py does not take
# --------------------------------------------------------------------------

def colour_stats(s: dict) -> dict:
    """
    Saturation, luminance distribution and clear-pixel share for one image.

    Reads the pixel buffer validate_sprite.measure() already decoded, so this
    costs one extra pass and no extra file read.
    """
    px, w, h = s["px"], s["w"], s["h"]
    n = w * h
    lum = [0] * 256
    drawn = sat = 0
    clear = 0
    for i in range(n):
        a = px[i * 4 + 3]
        if a == 0:
            clear += 1
            continue
        if a < ALPHA_SOLID:
            continue
        drawn += 1
        r, g, b = px[i * 4], px[i * 4 + 1], px[i * 4 + 2]
        mx, mn = max(r, g, b), min(r, g, b)
        if mx >= SAT_MIN_VALUE and (mx - mn) / mx >= SAT_MIN_CHROMA:
            sat += 1
        lum[(r * 299 + g * 587 + b * 114) // 1000] += 1

    return {
        "drawn": drawn,
        "clear_fraction": clear / n if n else 0.0,
        "saturated": sat,
        "saturated_fraction": sat / drawn if drawn else 0.0,
        "distinct_luma": sum(1 for c in lum if c),
        "mean_luma": (sum(i * c for i, c in enumerate(lum)) / drawn) if drawn else 0.0,
        "dark_fraction": (sum(lum[:16]) / drawn) if drawn else 0.0,
        "light_fraction": (sum(lum[240:]) / drawn) if drawn else 0.0,
        "luma": lum,
    }


def extra_checks(s: dict, c: dict, ref_c: dict | None = None) -> list[tuple[str, str]]:
    """
    The C8 checks that live only here. `s` is a validate_sprite.measure() dict,
    `c` its colour_stats(), `ref_c` the reference's colour_stats() if there is
    one. Returns [(level, message)].
    """
    out: list[tuple[str, str]] = []

    def add(level: str, msg: str) -> None:
        out.append((level, msg))

    # --- fully transparent pixels ------------------------------------------
    if c["clear_fraction"] <= 0.0:
        add(REJECT, "NOT ONE pixel is fully transparent. The file has an alpha "
                    "channel, so a naive 'has alpha' test passes it, but nothing "
                    "is actually cut out - this renders as a block, not a "
                    "silhouette.")
    elif c["clear_fraction"] < CLEAR_MIN_FRACTION:
        add(WARN, f"only {c['clear_fraction']:.2%} of the canvas is fully "
                  f"transparent (healthy art in this repo measures 41-90%). The "
                  f"cutout may not have taken.")

    # --- saturated pixels ---------------------------------------------------
    if c["saturated"]:
        frac = c["saturated_fraction"]
        msg = (f"{c['saturated']:,} drawn pixels ({frac:.2%}) are fully "
               f"saturated (value >= {SAT_MIN_VALUE}, chroma >= "
               f"{SAT_MIN_CHROMA:.0%}). Every shipping asset measured in this "
               f"repo has exactly ZERO. RimWorld's palette is muted; pure hue "
               f"reads as a different game's asset.")
        if frac > SAT_REJECT_FRACTION:
            add(REJECT, msg)
        elif frac > SAT_WARN_FRACTION:
            add(WARN, msg)
        else:
            add(WARN, msg + " Below the 0.1% noise floor, so probably a stray "
                            "highlight - look once and move on.")

    # --- value distribution -------------------------------------------------
    if c["drawn"] and c["distinct_luma"] < MIN_DISTINCT_LUMA:
        add(REJECT, f"only {c['distinct_luma']} distinct luminance level(s) "
                    f"among {c['drawn']:,} drawn pixels (real art measures "
                    f"93-247). This is a flat fill or a solid-colour "
                    f"placeholder, not a sprite.")
    if c["dark_fraction"] > CRUSHED_FRACTION:
        add(WARN, f"{c['dark_fraction']:.0%} of drawn pixels sit in the darkest "
                  f"16 luminance levels - the image is crushed to black and will "
                  f"read as a silhouette in game.")
    if c["light_fraction"] > BLOWN_FRACTION:
        add(WARN, f"{c['light_fraction']:.0%} of drawn pixels sit in the "
                  f"lightest 16 luminance levels - the image is blown out.")
    if ref_c is not None and c["drawn"] and ref_c["drawn"]:
        drift = c["mean_luma"] - ref_c["mean_luma"]
        if abs(drift) > MEAN_LUMA_DRIFT:
            add(WARN, f"mean luminance {c['mean_luma']:.0f} against the "
                      f"reference's {ref_c['mean_luma']:.0f} ({drift:+.0f} "
                      f"levels). It will not sit next to its siblings.")

    return out


def extra_for_path(path, reference=None) -> list[tuple[str, str]]:
    """
    The library entry point. Measure one file and return only the findings this
    module adds - saturation, value distribution, clear pixels - so another
    validator can bolt them on without inheriting this file's CLI or verdicts.

    Used by src/RimMandrake/WreckedMachines/Source/check_sprite.py, which keeps
    its own manifest-driven interface. Never raises: a decode failure comes back
    as a REJECT line, because a checker that throws mid-batch loses every
    result after it.
    """
    if not HAVE_VS:
        return []
    try:
        s = VS.measure(Path(path))
        c = colour_stats(s)
    except Exception as e:                           # noqa: BLE001
        return [(REJECT, f"could not measure: {e}")]
    ref_c = None
    if reference:
        try:
            ref_c = colour_stats(VS.measure(Path(reference)))
        except Exception:                            # noqa: BLE001
            ref_c = None
    return extra_checks(s, c, ref_c)


# --------------------------------------------------------------------------
# Facing parity — the check that needs two files at once
# --------------------------------------------------------------------------

def facing_parity(a_name: str, a: dict, b_name: str, b: dict) -> list[tuple[str, str]]:
    """
    Compare two facings of the same thing. Written for south vs north, which is
    what C8 asked for, but the maths is the same for any pair of facings that
    should share a footprint.
    """
    out: list[tuple[str, str]] = []

    def add(level: str, msg: str) -> None:
        out.append((level, f"{a_name} vs {b_name}: {msg}"))

    if (a["w"], a["h"]) != (b["w"], b["h"]):
        add(REJECT, f"canvases differ ({a['w']}x{a['h']} vs {b['w']}x{b['h']}). "
                    f"RimWorld draws every facing at the same drawSize, so one "
                    f"of them renders at the wrong scale.")
        return out

    if a["sha"] == b["sha"]:
        add(REJECT, "the two facings are pixel-identical. One is a copy of the "
                    "other and the thing will not turn.")

    if not a["bbox"] or not b["bbox"]:
        add(REJECT, "one of the facings has no visible subject, so the "
                    "silhouettes cannot be compared.")
        return out

    for label, av, bv in (("width", a["span_w"], b["span_w"]),
                          ("height", a["span_h"], b["span_h"])):
        drift = (bv - av) / av if av else 0.0
        if abs(drift) > PARITY_SPAN_TOLERANCE:
            level = REJECT if label == "width" else WARN
            add(level, f"drawn {label} {av}px vs {bv}px ({drift:+.0%}). The two "
                       f"facings show the same footprint from opposite sides, so "
                       f"they must span it alike; measured drift on healthy "
                       f"pairs in this repo is 0-2%.")

    for label, ai, bi, canvas in (("x", a["bbox"][0], b["bbox"][0], a["w"]),
                                  ("y", a["bbox"][1], b["bbox"][1], a["h"])):
        off = abs(bi - ai) / canvas
        if off > PARITY_ORIGIN_TOLERANCE:
            add(WARN, f"subject origin {label}={ai} vs {bi}, {off:.1%} of canvas "
                      f"apart. The thing will jump on screen as it is rotated.")

    if a["coverage"] > 0:
        ratio = b["coverage"] / a["coverage"]
        if not (PARITY_COVERAGE_LO <= ratio <= PARITY_COVERAGE_HI):
            add(WARN, f"drawn area ratio {ratio:.2f}. Some difference is normal - "
                      f"a back has less detail than a front - but this is beyond "
                      f"what a change of viewpoint explains.")

    return out


def facing_of(p: Path) -> tuple[str, str] | None:
    """('Foo', 'south') for Foo_south.png, else None. Masks (…m.png) ignored."""
    stem = p.stem
    for d in _FACINGS:
        if stem.endswith("_" + d):
            return stem[: -len(d) - 1], d
    return None


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------

def describe(path: Path, s: dict, c: dict) -> None:
    print(f"{path.name}")
    print(f"  canvas     {s['w']}x{s['h']}")
    print(f"  alpha      clear {c['clear_fraction']:.1%} of canvas | "
          f"drawn {c['drawn']:,} px ({s['coverage']:.2%})")
    if s["bbox"]:
        print(f"  subject    {s['span_w']}x{s['span_h']} at "
              f"({s['bbox'][0]},{s['bbox'][1]})")
    print(f"  colour     saturated {c['saturated']:,} px "
          f"({c['saturated_fraction']:.3%}) | distinct luma "
          f"{c['distinct_luma']} | mean {c['mean_luma']:.0f}")
    print(f"  value      dark {c['dark_fraction']:.1%} | "
          f"light {c['light_fraction']:.1%}")
    print(f"  corners    {s['corners']}")
    print(f"  sha256     {s['sha']}")


def parse_canvas(text: str) -> tuple[int, int]:
    for sep in ("x", "X", ","):
        if sep in text:
            a, _, b = text.partition(sep)
            return int(a), int(b)
    raise ValueError(f"cannot read a canvas size from {text!r}; use WxH")


def collect(targets: list[str]) -> list[Path]:
    out: list[Path] = []
    for t in targets:
        p = Path(t)
        if p.is_dir():
            out += sorted(q for q in p.rglob("*.png"))
        elif p.is_file():
            out.append(p)
        else:
            print(f"ERROR no such file or directory: {t}", file=sys.stderr)
            return []
    return out


def main() -> int:
    if not HAVE_VS:
        print(f"ERROR cannot import validate_sprite/pnglib from {_REPO}: "
              f"{_IMPORT_ERROR}", file=sys.stderr)
        return 2

    ap = argparse.ArgumentParser(
        description=__doc__.split("\n")[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="+",
                    help="PNG file(s) and/or directories to walk for *.png")
    ap.add_argument("--reference", default=None,
                    help="a known-good asset. Supplies the expected canvas and "
                         "the geometry every check is a ratio against. THIS, "
                         "not a constant, is where 512x512 comes from.")
    ap.add_argument("--canvas", default=None, metavar="WxH",
                    help="assert the canvas explicitly when there is no "
                         "reference asset to point at, e.g. 933x933.")
    ap.add_argument("--no-parity", action="store_true",
                    help="skip south/north facing parity")
    ap.add_argument("--describe", action="store_true",
                    help="print the numbers and no verdict")
    ap.add_argument("--strict", action="store_true",
                    help="treat warnings as rejections")
    args = ap.parse_args()

    files = collect(args.path)
    if not files:
        return 2

    want_canvas: tuple[int, int] | None = None
    if args.canvas:
        try:
            want_canvas = parse_canvas(args.canvas)
        except ValueError as e:
            print(f"ERROR {e}", file=sys.stderr)
            return 2

    ref = ref_c = None
    if args.reference:
        rp = Path(args.reference)
        if not rp.is_file():
            print(f"ERROR no such reference: {rp}", file=sys.stderr)
            return 2
        ref = VS.measure(rp)
        ref_c = colour_stats(ref)
        # ⚠️ Two sources of truth for the canvas, disagreeing, is exactly the C5
        # trap. Refuse rather than silently preferring one.
        if want_canvas and (ref["w"], ref["h"]) != want_canvas:
            print(f"ERROR --canvas says {want_canvas[0]}x{want_canvas[1]} but "
                  f"--reference {rp.name} is {ref['w']}x{ref['h']}. One of them "
                  f"is wrong; this will not guess.", file=sys.stderr)
            return 2
        want_canvas = (ref["w"], ref["h"])

    if want_canvas is None and not args.describe:
        print("  note   no --reference and no --canvas: canvas size is NOT "
              "checked. A sprite drawn at a placeholder's size passes this run "
              "and renders tiny in game (queue C5).")

    measured: dict[Path, tuple[dict, dict]] = {}
    rejects: list[str] = []
    warns: list[str] = []

    for p in files:
        try:
            s = VS.measure(p)
        except Exception as e:                       # noqa: BLE001
            print(f"\n{p.name}\n  REJECT unreadable PNG: {e}", file=sys.stderr)
            rejects.append(f"{p.name}: unreadable")
            continue
        c = colour_stats(s)
        measured[p] = (s, c)

        print()
        describe(p, s, c)
        if args.describe:
            continue

        findings: list[tuple[str, str]] = []
        if want_canvas and (s["w"], s["h"]) != want_canvas:
            findings.append((REJECT,
                             f"canvas is {s['w']}x{s['h']}, expected "
                             f"{want_canvas[0]}x{want_canvas[1]}. RimWorld draws "
                             f"against the def's drawSize, so this renders at "
                             f"the wrong scale."))
        if ref is not None and p.resolve() != Path(args.reference).resolve():
            findings += VS.check(ref, s)
        findings += extra_checks(s, c, ref_c)

        for level, msg in findings:
            print(f"  {level:<6} {msg}")
            (rejects if level == REJECT else warns).append(f"{p.name}: {msg}")

    # --- parity, across every _south/_north pair among the inputs -----------
    if not args.describe and not args.no_parity:
        groups: dict[str, dict[str, Path]] = {}
        for p in measured:
            got = facing_of(p)
            if got:
                groups.setdefault(got[0], {})[got[1]] = p
        for stem, facings in sorted(groups.items()):
            if "south" not in facings or "north" not in facings:
                continue
            sp, np_ = facings["south"], facings["north"]
            print(f"\nfacing parity: {stem}_south vs {stem}_north")
            found = facing_parity(sp.name, measured[sp][0],
                                  np_.name, measured[np_][0])
            if not found:
                print("  ok     silhouettes agree")
            for level, msg in found:
                print(f"  {level:<6} {msg}")
                (rejects if level == REJECT else warns).append(msg)

    if args.describe:
        return 0

    print()
    if rejects or (warns and args.strict):
        n = len(rejects) + (len(warns) if args.strict else 0)
        print(f"FAIL - {n} blocking problem(s) across {len(files)} file(s). "
              f"Do not put this in a mod.")
        return 1
    print(f"PASS - {len(files)} file(s) shippable"
          + (f" ({len(warns)} warning(s) - look at them)" if warns else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
