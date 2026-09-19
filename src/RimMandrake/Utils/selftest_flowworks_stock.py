#!/usr/bin/env python3
"""Wrapper for the C# selftest of the FlowWorks source stock model (§5).

`selftest_*.py` is the established convention for fast, offline, pre-commit
tests (see selftest_validate_patch.py for the canonical example, and
selftest_pit_logic.py for the other C# one). What this covers -
FlowWorks/Source/RM_StockMath.cs, the arithmetic of
design/RimMandrake/flowworks_mod_definition.md section 5's source stock model -
is C#, not Python, and this project has no xUnit/NUnit precedent. So the
actual test lives in a small standalone net8.0 console app needing no
RimWorld/Unity assemblies: FlowWorks/Source/SelfTest/.

WHAT MAKES THIS ONE STRONGER THAN ITS SIBLING: selftest_pit_logic.py's project
hand-extracts its escape-chance formula and says so in its header - it keeps
passing against the old formula if the real method changes. This project
extracts NOTHING. RM_StockMath.cs is the production file the shipping mod
compiles, pulled into the test project directly, so the 5:1 budget, the
seepage/rain/season refill, the supported-cell floor, the recession ordering
and the credit/debit primitives are all covered for real.

dotnet is WINDOWS-NATIVE (see RimMandrake_FlowWorks.csproj's own build comment)
and cannot take a /mnt/d path, so this script finds dotnet.exe and converts the
repo-relative project path to a D-drive-style path before invoking it.

    python3 selftest_flowworks_stock.py
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Utils -> RimMandrake -> src -> repo root.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CSPROJ = os.path.join(
    REPO, "src", "RimMandrake", "FlowWorks", "Source", "SelfTest",
    "RimMandrakeFlowWorks.SelfTest.csproj",
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
        sys.exit("RimMandrakeFlowWorks.SelfTest.csproj not found at %s — the "
                 "SelfTest project moved or was never built" % CSPROJ)

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
