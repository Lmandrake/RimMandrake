#!/usr/bin/env python3
"""Wrapper for the C# selftest of the covered-pit-trap math.

`selftest_*.py` is the established convention for fast, offline, pre-commit
tests (see selftest_validate_patch.py for the canonical example and why the
convention exists). The pieces this covers -
Trigger/PitCoverTier.cs's TriggerMassKg(), Escape/PitEscapeUtility.cs's
escape-chance formula, and the mass-sum-vs-threshold gate in
Trigger/CompPitCoverTrigger.cs's RunScan() - are C#, not Python, and this
project has no prior xUnit/NUnit precedent (checked: no *.Test*.csproj,
no PackageReference to any test framework anywhere under src/). Rather than
stand up a full test project layout, the actual test lives in a small
standalone net8.0 console app that needs no RimWorld/Unity assemblies -
Pits/Source/SelfTest/ (see that project's own header for exactly
what it compiles in for real vs. what it had to hand-extract because the
real method needs a live Pawn/Map). This script is just the one-line,
`python3 selftest_pit_logic.py`-shaped door into it, so it slots into the
same "loop over every selftest_*.py" habit as everything else here.

dotnet is WINDOWS-NATIVE (see Pits.csproj's own build comment)
and cannot take a /mnt/d path, so this script finds dotnet.exe and converts
the repo-relative project path to a D-drive-style path before invoking it.

    python3 selftest_pit_logic.py
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Utils -> RimMandrake -> src -> repo root.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CSPROJ = os.path.join(
    REPO, "src", "RimMandrake", "Pits", "Source", "SelfTest",
    "RimMandrakePits.SelfTest.csproj",
)

DOTNET_CANDIDATES = [
    "/mnt/c/Users/Mandrake/.dotnet/dotnet.exe",
    "/mnt/c/Program Files/dotnet/dotnet.exe",
]


def _find_dotnet():
    for c in DOTNET_CANDIDATES:
        if os.path.isfile(c):
            return c
    return None


def _to_windows_path(posix_path):
    """/mnt/d/Luke/... -> D:\\Luke\\... . dotnet.exe cannot resolve /mnt/*."""
    p = os.path.abspath(posix_path)
    if p.startswith("/mnt/") and len(p) > 6 and p[6] == "/":
        drive = p[5].upper()
        rest = p[7:].replace("/", "\\")
        return "%s:\\%s" % (drive, rest)
    return p.replace("/", "\\")


def main():
    if not os.path.isfile(CSPROJ):
        sys.exit("RimMandrakePits.SelfTest.csproj not found at %s — the SelfTest "
                  "project moved or was never built" % CSPROJ)

    dotnet = _find_dotnet()
    if dotnet is None:
        sys.exit(
            "dotnet.exe not found at any of %r — this selftest needs the "
            "user-local Windows-side .NET SDK (see CLAUDE.md's C# build "
            "toolchain note); UNMEASURED, not a pass or a fail" % DOTNET_CANDIDATES)

    win_csproj = _to_windows_path(CSPROJ)
    cmd = [dotnet, "run", "--project", win_csproj, "-c", "Release"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout, end="")
    if result.stderr.strip():
        print(result.stderr, end="", file=sys.stderr)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
