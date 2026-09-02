#!/usr/bin/env python3
"""Wrapper for the C# selftest of the RM_Property fabric
(PROPERTY_FABRIC_BUILD_1: src/RimMandrake/Property/Source/).

`selftest_*.py` is the established convention for fast, offline, pre-commit
tests (see selftest_validate_patch.py for the canonical example and why the
convention exists). The pieces this covers - ClaimDecay's pure decay math,
ClaimantRef's equality contract, and ClaimEngine's own private
strength/specificity/recency claim-resolution order - are C#, not Python.
The actual test lives in a small standalone net472 console app -
Property/Source/SelfTest/ (see that project's own .csproj/Program.cs
headers for exactly what compiles the REAL production source in directly
vs. what had to be extracted, and why PropertyEngine/ClaimEngine.
ResolveClaim's own PUBLIC surface has nothing left to test offline - every
entry point no-ops with no live Game). This script is just the one-line,
`python3 selftest_property_fabric.py`-shaped door into it, so it slots into
the same "loop over every selftest_*.py" habit as everything else here.

dotnet is WINDOWS-NATIVE and cannot take a /mnt/d path, so this script
finds dotnet.exe and converts the repo-relative project path to a
D-drive-style path before invoking it.

    python3 selftest_property_fabric.py
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Utils -> RimMandrake -> src -> repo root.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CSPROJ = os.path.join(
    REPO, "src", "RimMandrake", "Property", "Source", "SelfTest",
    "RimMandrakeProperty.SelfTest.csproj",
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
        sys.exit("RimMandrakeProperty.SelfTest.csproj not found at %s — the SelfTest "
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
