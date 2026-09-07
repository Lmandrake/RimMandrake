#!/usr/bin/env python3
"""selftest_tool_metadata.py - the DLL's [Tool] surface must equal the source's.

WHY THIS EXISTS
================
BUILD_PY_TOOLNAME_SCAN_FALSE_LOSS_1, 2026-09-06: build.py's tool-removal guard
used to byte-scan a compiled DLL for `jawa/[a-z_]{3,40}` after decoding the
whole file as UTF-16LE and UTF-8. That can truncate a real name (reported
live as a fictitious lost tool, `jawa/pawn_`, which was really a
prefix-truncated read of a real, still-present name) and can also match a
name merely MENTIONED in another tool's Description prose (`jawa/revoke`).
tool_metadata.py replaced it with an exact CustomAttribute-table read.

This is the regression test for that fix, and it is deliberately built to
compare against the SOURCE declarations rather than a previous scan --
"a scan that passes because both sides are wrong the same way" is exactly
the failure mode a self-comparison would let through.

WHAT IT NEEDS
=============
A locally built companion DLL (src/RimMandrake/bridgetools/artifacts/...),
which needs `dotnet` and, per build.py's own refusal, Windows Python -- not
guaranteed to exist in every checkout or CI box. When it is missing this
SKIPS (exit 2) rather than failing the whole suite; run
`python.exe src/RimMandrake/bridgetools/build.py --gm` first to produce one.

    python3 src/RimMandrake/bridgetools/selftest_tool_metadata.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build            # noqa: E402  (GM_TOOLS, ARTIFACT_DIR, DLL_NAME)
import tool_metadata     # noqa: E402

SOURCE_DIR = os.path.join(HERE, "JawaBench.BridgeTools")
DLL_PATH = os.path.join(build.ARTIFACT_DIR, build.DLL_NAME)

# Stated in the item that created this test, 2026-09-06 -- reported, never
# asserted against blindly: the source is the ground truth, this number is
# only a sanity trip-wire for "did the roster move a lot without me noticing".
EXPECTED_COUNT_AS_OF_FILING = 313


def main():
    if not os.path.isdir(SOURCE_DIR):
        print("FAIL - source dir not found: %s" % SOURCE_DIR)
        return 1

    source_set = tool_metadata.tool_names_from_source(SOURCE_DIR)
    print("source declares %d tools (%d at filing time; drift is expected, "
          "not a failure)" % (len(source_set), EXPECTED_COUNT_AS_OF_FILING))
    if not source_set:
        print("FAIL - source scan found zero [Tool(...)] declarations -- "
              "the regex or the source path is broken, not the roster")
        return 1

    if not os.path.exists(DLL_PATH):
        print("SKIP - no local build at %s\n"
              "  run: python.exe %s --gm" % (DLL_PATH,
              os.path.join(HERE, "build.py")), file=sys.stderr)
        return 2

    dll_set = tool_metadata.tool_names_from_dll(DLL_PATH)
    if not dll_set:
        print("FAIL - metadata read found zero tools in a real DLL -- "
              "the reader is broken, not the roster")
        return 1

    gm = set(build.GM_TOOLS)
    gm_present = gm & dll_set
    if gm_present and gm_present != gm:
        print("FAIL - GM pair is PARTIALLY present in the DLL (%s) -- "
              "build.py's own verify_gm_gate should already refuse this build"
              % sorted(gm_present))
        return 1

    expected = source_set if gm_present == gm else (source_set - gm)
    missing = sorted(expected - dll_set)
    extra = sorted(dll_set - expected)
    ok = not missing and not extra

    if not ok:
        print("FAIL - DLL tool surface != source declarations "
              "(built %s GM pair)" % ("WITH" if gm_present == gm else "WITHOUT"))
        if missing:
            print("  declared in source, absent from DLL: %s" % ", ".join(missing))
        if extra:
            print("  in DLL, not declared in source (phantom/truncation?): %s"
                  % ", ".join(extra))
        return 1

    print("ok    DLL tool surface == source declarations, %d tools "
          "(GM pair %s)" % (len(dll_set), "included" if gm_present == gm else "excluded"))
    print("\n1/1 passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
