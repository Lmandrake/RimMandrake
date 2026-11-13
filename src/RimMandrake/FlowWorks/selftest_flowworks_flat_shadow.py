#!/usr/bin/env python3
"""RIMMANDRAKE_REMOVE_DARK_SQUARE_AROUND_SUNK_GEYSER_UNWELCOME_BOX: no hard dark box under flat things in a pit.

Owner, 2026-11-12: "In geyser_pit.png you can see a strange darker square around the geyser image that isn't welcome."
The square was RM_SubmergeDraw.FloorShadow: a white-texture quad the size of the footprint, drawn for every building
standing in a pit. Since 1eaef24497 a sunk geyser is left out; this keeps it so and extends it:
  - a flat thing (fillPercent under RM_UnderLiquid.FlatFillPercent, no vanilla sun shadow, no shadowData) casts none;
  - every floor shadow is a feathered texture (RM_UnderLiquid.ShadowFeather), never BaseContent.WhiteTex.
The numbers are proved by the C# case UnderLiquid_flat_things_cast_no_floor_shadow_and_edges_are_soft
(selftest_flowworks_stock.py); this checks the wiring in the source.

CAN IT FAIL: each wire taken out of a copy of the source must go red (run at the end).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "Source"
sys.path.insert(0, str(HERE))
from selftest_flowworks_underliquid_parity import mask_comments, method_body  # noqa: E402


def checks(ul: str, draw: str, tests: str) -> list[tuple[str, bool]]:
    ul, draw = mask_comments(ul), mask_comments(draw)
    casts = method_body(ul, r"public static bool CastsFloorShadow\(float fillPercent, float sunShadowHeight, bool hasShadowData\)")
    m = re.search(r"\bconst\s+float\s+FlatFillPercent\s*=\s*([0-9.]+)f\s*;", ul)
    feather = method_body(ul, r"public static float ShadowFeather\(float u, float v\)")
    floor = method_body(draw, r"internal static void FloorShadow\(SectionLayer layer\)")
    mat = method_body(draw, r"private static Material ShadowMat\(int q\)")
    begin = method_body(draw, r"public static void Begin\(Thing t\)")
    return [
        ("RM_UnderLiquid.CastsFloorShadow exists", bool(casts)),
        ("FlatFillPercent is a small fill (0.1..0.3)", bool(m) and 0.1 <= float(m.group(1)) <= 0.3),
        ("CastsFloorShadow reads the fill, the sun shadow and shadowData",
         all(s in casts for s in ("FlatFillPercent", "sunShadowHeight", "hasShadowData"))),
        ("RM_UnderLiquid.ShadowFeather exists", bool(feather)),
        ("FloorShadow asks CastsFloorShadow with the def's fill, sun shadow and shadowData",
         "RM_UnderLiquid.CastsFloorShadow(" in floor and "fillPercent" in floor and "staticSunShadowHeight" in floor
         and "shadowData" in floor),
        ("the floor shadow is not a white-texture box", bool(mat) and "WhiteTex" not in mat and "FeatherTex" in mat),
        ("the feathered texture is built from ShadowFeather", "RM_UnderLiquid.ShadowFeather(" in draw),
        ("a sunk geyser still opens no floor shadow", "!(t is Building_SteamGeyser)" in begin),
        ("the C# case is wired", "UnderLiquid_flat_things_cast_no_floor_shadow_and_edges_are_soft" in tests),
    ]


def run(rows) -> int:
    bad = 0
    for name, ok in rows:
        print(("PASS " if ok else "FAIL ") + name)
        bad += not ok
    return bad


def main() -> int:
    ul = (SRC / "Superdeep" / "RM_UnderLiquid.cs").read_text(encoding="utf-8")
    draw = (SRC / "Superdeep" / "RM_SubmergeDraw.cs").read_text(encoding="utf-8")
    tests = (SRC / "SelfTest" / "UnderLiquidParityChecks.cs").read_text(encoding="utf-8")
    bad = run(checks(ul, draw, tests))
    # can-fail: each wire spliced out must turn at least one row red
    plants = [
        ("FloorShadow ignores CastsFloorShadow", ul, draw.replace("RM_UnderLiquid.CastsFloorShadow(", "RM_UnderLiquid.Ignored(")),
        ("ShadowMat back on WhiteTex", ul, draw.replace("FeatherTex", "BaseContent.WhiteTex")),
        ("geyser exclusion removed", ul, draw.replace("!(t is Building_SteamGeyser)", "true")),
        ("flat fill raised to 0.5", re.sub(r"FlatFillPercent\s*=\s*[0-9.]+f", "FlatFillPercent = 0.5f", ul), draw),
        ("feather dropped", ul.replace("public static float ShadowFeather(float u, float v)", "public static float Gone(float u, float v)"), draw),
    ]
    for name, u2, d2 in plants:
        caught = any(not ok for _, ok in checks(u2, d2, tests))
        print(("PASS " if caught else "FAIL ") + "can-fail: " + name + " goes red")
        bad += not caught
    print("RESULT", "GREEN" if not bad else "RED %d" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
