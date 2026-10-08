#!/usr/bin/env python3
"""Approach B fuzz of the FloodedCanyon kernels (FloodedCanyon/Source/Kernel/*.cs), no game.

Seeded fuzz over the production kernels with explicit invariants: the flood-cycle phase machine with its beats, chimes, jitter
and peakstorm pull (flood), the flood's spread / ledger / chime geometry (cells), the ledge refuge (refuge), the sleeper pan state
machine (pan), and the aftermath timers / biome score / fossil strata geometry against independent oracles (rules). Built through
winbuild.stage_build (dotnet.exe is Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_floodedcanyon_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only flood|cells|refuge|pan|rules]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "FloodedCanyon", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeFloodedCanyon.SelfTest.csproj")


def source_guards():
    """Component-level regressions the Verse-free kernel cannot see (text scan of the production component)."""
    import re
    src = open(os.path.join(REPO, "src", "RimMandrake", "FloodedCanyon", "Source", "RM_MapComponent_CanyonFlood.cs"), encoding="utf-8").read()
    bad = []
    # CANYON_FLOOD_ROAR_SILENT_1: MaintainRoar has a live caller in MapComponentTick
    tick = src[src.index("public override void MapComponentTick()"):]
    tick = tick[:tick.index("private static int HoursToTicks")]
    if "MaintainRoar()" not in tick:
        bad.append("CANYON_FLOOD_ROAR_SILENT_1: MapComponentTick never calls MaintainRoar()")
    # FLOOD_LEDGER_LOAD_LOSS_1: scribed ledger lists are fields, never locals re-nulled each load phase
    expose = src[src.index("public override void ExposeData()"):]
    for name in ("activeFloodCells", "raisedFillCells", "raisedFillPrior"):
        if re.search(r"List<\w+>\s+[^;]*\b" + name + r"\s*=\s*null", expose):
            bad.append("FLOOD_LEDGER_LOAD_LOSS_1: " + name + " is a local in ExposeData (lost between load phases)")
        if not re.search(r"private List<\w+>[^;]*\b" + name + r"\b", src[:src.index("public override void ExposeData()")]):
            bad.append("FLOOD_LEDGER_LOAD_LOSS_1: " + name + " is not a field")
    for b in bad:
        print("SOURCE GUARD FAILED:", b)
    return 1 if bad else 0


def main(argv):
    if source_guards():
        return 1
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="FloodedCanyonFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "FloodedCanyon", "Source", "Kernel"), os.path.join(REPO, "src", "RimMandrake", "FloodedCanyon", "Source")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeFloodedCanyon.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
