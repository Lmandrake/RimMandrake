#!/usr/bin/env python3
"""Wrapper for the C# selftest of the Stillsand precious caves
(STILLSAND_PRECIOUS_CAVES_1, src/RimMandrake/Stillsand/Source/RM_PreciousCaveGeometry.cs).
Same shape as selftest_sun_heat.py. Covers the compass word, the yardang shape,
the depth map / chamber placement, the shade-face mouth (on ten synthetic rocks
the mouth must face away from the sun) and the weighted table roll. What it
cannot cover (the carve against a real map, the spawned contents, the letter)
is the live quicktest owed by STILLSAND_PRECIOUS_CAVES_LIVE_1.

dotnet is WINDOWS-NATIVE and cannot take a /mnt/d path, so this script finds
dotnet.exe and converts the project path to a D-drive-style path first.

    python3 selftest_precious_caves.py
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Utils -> RimMandrake -> src -> repo root.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CSPROJ = os.path.join(
    REPO, "src", "RimMandrake", "Stillsand", "Source", "SelfTest",
    "RimMandrakeStillsand.PreciousCaves.SelfTest.csproj",
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
        sys.exit("PreciousCaves SelfTest csproj not found at %s" % CSPROJ)
    dotnet = _find_dotnet()
    if dotnet is None:
        sys.exit(
            "dotnet.exe not found at any of %r — this selftest needs the "
            "user-local Windows-side .NET SDK; UNMEASURED, not a pass or a fail"
            % DOTNET_CANDIDATES)
    cmd = [dotnet, "run", "--project", _to_windows_path(CSPROJ), "-c", "Release"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout, end="")
    if result.stderr.strip():
        print(result.stderr, end="", file=sys.stderr)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
