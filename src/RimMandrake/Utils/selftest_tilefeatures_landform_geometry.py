#!/usr/bin/env python3
"""Wrapper for the C# selftest of mandrake.rm.tilefeatures' landform geometry
(VEE_LANDFORMS_BUILD_CRATERS_AND_COMPANY: src/RimMandrake/TileFeatures/Source/SelfTest/).

Compiles production RM_LandformGeometry.cs (no game types) with Program.cs and runs it: crater zones and breaches,
meanders and distances, the ridge band with a gap, disc placement and the tide, with two raster walkability checks that
each carry a planted negative. See SelfTest/Program.cs's header for what is and is not covered.

dotnet is WINDOWS-NATIVE and cannot take an ext4 path, so the project is staged with selftest_winstage
(whole_src=False: it reads no shipped file beyond its own two sources).

    python3 selftest_tilefeatures_landform_geometry.py
"""
from __future__ import annotations

import os
import subprocess
import sys

from selftest_winstage import windows_project_path

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CSPROJ = os.path.join(REPO, "src", "RimMandrake", "TileFeatures", "Source", "SelfTest",
                      "RimMandrakeTileFeatures.SelfTest.csproj")

DOTNET_CANDIDATES = [
    "/mnt/c/Users/Mandrake/.dotnet/dotnet.exe",
    "/mnt/c/Program Files/dotnet/dotnet.exe",
]


def main():
    if not os.path.isfile(CSPROJ):
        sys.exit("RimMandrakeTileFeatures.SelfTest.csproj not found at %s" % CSPROJ)
    dotnet = next((c for c in DOTNET_CANDIDATES if os.path.isfile(c)), None)
    if dotnet is None:
        sys.exit("dotnet.exe not found at any of %r; UNMEASURED, not a pass or a fail" % DOTNET_CANDIDATES)
    win_csproj = windows_project_path(CSPROJ, whole_src=False)
    result = subprocess.run([dotnet, "run", "--project", win_csproj, "-c", "Release"], capture_output=True, text=True)
    print(result.stdout, end="")
    if result.stderr.strip():
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode == 0 and "0 failed" not in result.stdout:
        sys.exit("dotnet exited 0 but printed no '0 failed' summary: the test program did not run to its end")
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
