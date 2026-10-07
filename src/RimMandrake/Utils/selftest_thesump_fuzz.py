#!/usr/bin/env python3
"""Approach B fuzz of The Sump kernels (src/RimMandrake/TheSump/Source/Kernel/RM_SumpKernel.cs), no game.

Seeded fuzz with explicit invariants: the kethrel's scrap-shell decisions through a fake world with probe order checked (kethrel), the
tar vault's seal ledger and solvent economy (vault) and the Deep Black mere's randomized flood fill on random grids (mere). Built through
winbuild.stage_build (dotnet.exe is Windows-native), then run. The older XML check is src/RimMandrake/TheSump/selftest_tar_filth_flags.py.

    python3 src/RimMandrake/Utils/selftest_thesump_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only kethrel|vault|mere]

A failing case is shrunk and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "TheSump", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeTheSump.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="TheSumpFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "TheSump", "Source", "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeTheSump.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
