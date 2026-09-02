#!/usr/bin/env python3
"""Wrapper for the C# selftest of GameComponent_ColonyVisibility
(COLONY_VISIBILITY_BUILD_1: src/RimMandrake/Visibility/Source/
GameComponent_ColonyVisibility.cs).

Same shape as selftest_pit_logic.py, same reason: `selftest_*.py` is this
project's established fast, offline, pre-commit test convention (see
selftest_validate_patch.py), but the 0-100 -> five-band ladder and the
Adjust()/ResetOnLaunch() clamps are C#, not Python, and there is still no
xUnit/NUnit precedent anywhere under src/. The actual test is a standalone
net48 console app - RimMandrake/Visibility/Source/SelfTest/ - that compiles
the REAL GameComponent_ColonyVisibility.cs in directly (see that project's
own header for exactly what is real vs. what a bare, no-game process cannot
do, and how the one native-engine snag - Verse.Log.Message needing a real
Unity runtime - was worked around without touching the production logic).
This script is just the `python3 selftest_colony_visibility.py`-shaped door
into it.

Relocated 2026-09-02 (FOUNDRY): COLONY_VISIBILITY_BUILD_1 rehomed the real
class from src/RimUtinni/Doctrine/Source/DoctrineCore/ColonyVisibility.cs
into its own dedicated mod without moving this test, which silently broke
(CS2001, source file not found) until this pass fixed it.

dotnet is WINDOWS-NATIVE and cannot take a /mnt/d path, so this script
finds dotnet.exe and converts the repo path to a D-drive-style path first.

    python3 selftest_colony_visibility.py
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Utils -> RimMandrake -> src -> repo root.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CSPROJ = os.path.join(
    REPO, "src", "RimMandrake", "Visibility", "Source", "SelfTest",
    "RimMandrakeVisibility.SelfTest.csproj",
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
        sys.exit("RimMandrakeVisibility.SelfTest.csproj not found at %s — the SelfTest "
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
