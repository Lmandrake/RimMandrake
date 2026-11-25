"""How deep does a drawn pit read, against how deep it is? (RIMMANDRAKE_DEEPEN_FLOWWORKS_PIT_LOOK_HE_SUSPECTS_READS_SHALLOW)

For one-depth 3x3 pits of 2 to 16 m, each depth cue that the build draws is turned back into the depth it shows, on the
game's own scales:

  north face   the drawn north inner wall (ladder.H, squares) against a standing colonist drawn beside it. A colonist is
               PAWN_SQUARES tall on screen [measured, live capture]; a person is PERSON_M tall [assumed]. So one square of
               upright draw shows UPRIGHT_M metres, and a face of H squares shows H x UPRIGHT_M metres.
  cast shadow  the drawn shadow past the north face's foot at the pick's sun (pitrule: SHADOW_K x z^SHADOW_POW squares at
               slope 1 = sun elevation SUN_EL). A wall of depth d casts d / tan(SUN_EL) metres = that / SQUARE_M squares, so a
               drawn shadow of s squares shows s x SQUARE_M x tan(SUN_EL) metres.
  floor in view the share of the 3-square pit's north-south span that shows floor (3 - H) / 3, against the share that the
               colonist's upright scale would leave (3 - z / UPRIGHT_M) / 3, never under 0.
  tone         the floor's tone (ladder.K) and its CIE L* step from the depth before; tone has no metre scale.

    python3 design/specs/2026-11-25-pit-reads-as-deep/measure.py            # writes table.md and readings.json beside it
    python3 design/specs/2026-11-25-pit-reads-as-deep/measure.py --check    # writes nothing; exit 1 when a reading is missing
                                                                             # or the offline twin has drifted from the C# build

Exit 0: every depth has a reading from every cue, and the twin's constants equal the build's. Exit 1: a reading is
missing or the twin drifted (the readings would describe a look that is not shipped). Exit 2: an input could not be read.
Pure arithmetic: no game, no Verse.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-22-stepped-pit-inner-cliff"))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-23-pit-floor-depth-ladder"))
import ladder  # noqa: E402
import pitrule  # noqa: E402

CS = os.path.join(ROOT, "src", "RimMandrake", "FlowWorks", "Source", "RM_PitReliefMath.cs")

DEPTHS = (2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 16.0)
PIT_SQUARES = 3          # the live look's one-depth pits are 3x3
SQUARE_M = math.sqrt(2)  # a square is 2 m^2, 1.41 m a side (design/RimMandrake/flowworks_unified_depth_2026-10-17.md)
# The colonist beside the 2 m pit in after_ladder_close_02m.png (RIMMANDRAKE_FIX_PIT_FLOOR_TINT_PAST_TWO_M_DRAWS_ONE_COLOUR,
# ArchBig 2026-11-23): outline rows 169..288 (120 px, feet to hair) against the pit frame 282..562 (280 px for 3 squares,
# 93.3 px a square) [measured 2026-11-25, dark-pixel rows < 25 grey].
PAWN_SQUARES = 120.0 / (280.0 / 3.0)
PERSON_M = 1.75          # a standing adult [assumed]
UPRIGHT_M = PERSON_M / PAWN_SQUARES


def build_constants() -> dict:
    """The C# build's shadow and north-face constants, read from the source."""
    src = open(CS, encoding="utf-8").read()
    out = {}
    m = re.search(r"ShadowK\s*=\s*([0-9.]+)f\s*,\s*ShadowPow\s*=\s*([0-9.]+)f", src)
    if m:
        out["ShadowK"], out["ShadowPow"] = float(m.group(1)), float(m.group(2))
    m = re.search(r"StepHSlope\s*=\s*([0-9.]+)\s*,\s*StepHLog\s*=\s*([0-9.]+)", src)
    if m:
        out["StepHSlope"], out["StepHLog"] = float(m.group(1)), float(m.group(2))
    m = re.search(r"SunElevation\s*=\s*([0-9.]+)f", src)
    if m:
        out["SunElevation"] = float(m.group(1))
    return out


def drift(build: dict) -> list[str]:
    twin = {"ShadowK": pitrule.SHADOW_K, "ShadowPow": pitrule.SHADOW_POW, "StepHSlope": ladder.H_SLOPE,
            "StepHLog": ladder.H_LOG, "SunElevation": pitrule.SUN_EL}
    bad = []
    for k, v in twin.items():
        if k not in build:
            bad.append("%s: not found in %s" % (k, os.path.relpath(CS, ROOT)))
        elif abs(build[k] - v) > 1e-9:
            bad.append("%s: build %s, twin %s" % (k, build[k], v))
    return bad


def row(z: float, z_prev: float | None) -> dict:
    tan_el = math.tan(math.radians(pitrule.SUN_EL))
    face = ladder.H(z)
    shadow = pitrule.SHADOW_K * z ** pitrule.SHADOW_POW
    true_shadow = z / tan_el / SQUARE_M
    floor_drawn = max(0.0, (PIT_SQUARES - face) / PIT_SQUARES)
    floor_true = max(0.0, (PIT_SQUARES - z / UPRIGHT_M) / PIT_SQUARES)
    k = ladder.K(z)
    dl = None if z_prev is None else ladder.floor_lstar(ladder.K(z_prev)) - ladder.floor_lstar(k)
    return {
        "depth_m": z,
        "face_squares": round(face, 3),
        "face_vs_colonist": round(face / PAWN_SQUARES, 3),
        "face_reads_m": round(face * UPRIGHT_M, 2),
        "shadow_squares": round(shadow, 3),
        "shadow_true_squares": round(true_shadow, 2),
        "shadow_reads_m": round(shadow * SQUARE_M * tan_el, 2),
        "floor_in_view_drawn": round(floor_drawn, 2),
        "floor_in_view_true": round(floor_true, 2),
        "tone": round(k, 3),
        "floor_lstar": round(ladder.floor_lstar(k), 1),
        "lstar_step_from_previous": None if dl is None else round(dl, 1),
    }


def main(argv: list[str]) -> int:
    check = "--check" in argv
    try:
        build = build_constants()
    except OSError as e:
        print("COULD NOT LOOK: %s" % e)
        return 2
    bad = drift(build)
    rows, prev = [], None
    for z in DEPTHS:
        rows.append(row(z, prev))
        prev = z
    missing = [r["depth_m"] for r in rows if any(v is None for kk, v in r.items() if kk != "lstar_step_from_previous")]

    lines = [
        "| true depth | north face (squares) | face / colonist | face reads as | shadow drawn (sq) | shadow true (sq) |"
        " shadow reads as | floor in view, drawn | floor in view, true | floor L* (step) |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        step = "" if r["lstar_step_from_previous"] is None else " (-%s)" % r["lstar_step_from_previous"]
        lines.append("| %g m | %.2f | %.2f | %.1f m | %.2f | %.1f | %.1f m | %d%% | %d%% | %.1f%s |" % (
            r["depth_m"], r["face_squares"], r["face_vs_colonist"], r["face_reads_m"], r["shadow_squares"],
            r["shadow_true_squares"], r["shadow_reads_m"], round(100 * r["floor_in_view_drawn"]),
            round(100 * r["floor_in_view_true"]), r["floor_lstar"], step))
    scale = ("Scales: a colonist draws %.2f squares tall [measured]; a person is %.2f m [assumed]; so one upright square "
             "shows %.2f m. A square is %.2f m a side. Sun elevation %g degrees (the pick's sun, slope 1)." % (
                 PAWN_SQUARES, PERSON_M, UPRIGHT_M, SQUARE_M, pitrule.SUN_EL))
    if check:
        if bad:
            print("DRIFT: the offline twin is not the build: " + "; ".join(bad))
        if missing:
            print("MISSING: no reading at " + ", ".join("%g m" % z for z in missing))
        if bad or missing:
            return 1
        print("MEASURED: %d depths, 4 cues, twin equals build" % len(rows))
        return 0
    with open(os.path.join(HERE, "table.md"), "w", encoding="utf-8") as f:
        f.write("<!-- written by measure.py; do not edit by hand -->\n" + "\n".join(lines) + "\n\n" + scale + "\n")
    with open(os.path.join(HERE, "readings.json"), "w", encoding="utf-8") as f:
        json.dump({"scales": {"pawn_squares": round(PAWN_SQUARES, 3), "person_m": PERSON_M,
                              "upright_m_per_square": round(UPRIGHT_M, 3), "square_m": round(SQUARE_M, 3),
                              "sun_elevation_deg": pitrule.SUN_EL},
                   "build_constants": build, "drift": bad, "rows": rows}, f, indent=1)
        f.write("\n")
    print("\n".join(lines))
    print(scale)
    if bad:
        print("DRIFT: the offline twin is not the build: " + "; ".join(bad))
    if missing:
        print("MISSING: no reading at " + ", ".join("%g m" % z for z in missing))
    print("MEASURED: %d depths, 4 cues" % len(rows) + ("" if not bad else ", with drift (run --check)"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
