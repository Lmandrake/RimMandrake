#!/usr/bin/env python3
"""Approach B fuzz of the TerminalBiomes kernels (TerminalBiomes/Source/Kernel/*.cs), no game.

Seeded fuzz over the production kernels with explicit invariants: the drifting light-well book (wells), the sun sphere
culture clock (sphere), the channel current field, cadence, drift step and surge grab (channel), the Grey Sea hull
crust clock (crust), the grey lamp watch (lamp) and the small rules (misc: Sunk, wax procession, veil fall). The project
is built through winbuild.stage_build (dotnet.exe is Windows-native), then run.

    python3 src/RimMandrake/Utils/selftest_terminalbiomes_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only wells|sphere|channel|crust|lamp|misc]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "TerminalBiomes", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeTerminalBiomes.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="TerminalBiomesFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "TerminalBiomes", "Source", "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeTerminalBiomes.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
