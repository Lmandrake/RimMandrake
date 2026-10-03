#!/usr/bin/env python3
"""Wrapper for the C# selftest of the furnace-beast warmth maths (PYRELANDS_FURNACE_WARMTH_AMBIENT_1,
src/RimMandrake/Pyrelands/Source/FurnaceWarmthMath.cs). Same shape as selftest_sun_heat.py.

    python3 selftest_furnace_warmth.py
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Utils -> RimMandrake -> src -> repo root.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CSPROJ = os.path.join(
    REPO, "src", "RimMandrake", "Pyrelands", "Source", "SelfTest",
    "RimMandrakePyrelands.FurnaceWarmth.SelfTest.csproj",
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
        sys.exit("FurnaceWarmth SelfTest csproj not found at %s — the SelfTest "
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
