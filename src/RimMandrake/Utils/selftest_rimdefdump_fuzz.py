#!/usr/bin/env python3
"""Approach B fuzz of the RimDefDump JSON writer and capture/stem kernel (Source/JsonWriter.cs, Source/Kernel/RM_DumpKernel.cs), no game.

Seeded fuzz: random object/array/string/number trees written indented and compact and read back by an independent strict reader (every control
character, quote, backslash, surrogate pair and lone surrogate), float/double/long/ulong round trips (no widening noise, NaN -> null, ulong exact),
unique case-insensitive def-type file stems, and capture-id vocabulary plus retention (newest three unfrozen kept, frozen and junk never touched).
Built through winbuild.stage_build, then run.

    python3 src/RimMandrake/Utils/selftest_rimdefdump_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only json|numbers|stems|captures]

A failing case prints `family seed N: message`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

MOD = os.path.join(REPO, "src", "RimMandrake", "RimDefDump", "Source")
SELFTEST = os.path.join(MOD, "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeRimDefDump.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="RimDefDumpFuzz", extra_dirs=[os.path.join(MOD, "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeRimDefDump.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
