#!/usr/bin/env python3
"""Wrapper for the C# selftest of StatPart_InverseBodySize
(OTHER_STUN_WEAPONS_SURVEY_1 / ION_STUN_IGNORES_BODY_SIZE_1:
src/RimStarWars/JawaIonWeapons/Source/StatPart_InverseBodySize.cs).

Same shape as selftest_pit_logic.py and selftest_colony_visibility.py, same
reason: `selftest_*.py` is this project's established fast, offline,
pre-commit test convention (see selftest_validate_patch.py), the tested
logic is C# not Python, and there is still no xUnit/NUnit precedent under
src/. The actual test is a standalone net472 console app -
JawaIonWeapons/SelfTest/ - that compiles the REAL StatPart_InverseBodySize
class in directly for its not-a-Pawn guard clause, and separately locks in
the 25x (Rat/Human) and 1024x (Human/Behemoth) stun-severity scaling ratios
measured live this session, via an extracted transcription of the transform
(constructing a live Pawn with a controlled BodySize is not viable offline
- see that project's own Program.cs header for exactly what is real vs.
extracted and why).

dotnet is WINDOWS-NATIVE and cannot take a /mnt/d path, so this script
finds dotnet.exe and converts the repo path to a D-drive-style path first.

    python3 selftest_stun_scaling.py
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Utils -> RimMandrake -> src -> repo root.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CSPROJ = os.path.join(
    REPO, "src", "Jawa", "JawaIonWeapons", "Source", "SelfTest",
    "JawaIonWeapons.SelfTest.csproj",
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
        sys.exit("JawaIonWeapons.SelfTest.csproj not found at %s — the SelfTest "
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
