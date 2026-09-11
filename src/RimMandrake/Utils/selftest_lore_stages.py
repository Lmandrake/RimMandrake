#!/usr/bin/env python3
"""Wrapper for the C# selftest of mandrake.rm.lorestages
(STAGED_LORE_BUILD_1: src/RimMandrake/LoreStages/Source/).

Same shape as selftest_aftermath.py. What the C# proves, and why it needs the
real Assembly-CSharp.dll rather than a mock:

  * `ThingDef.descriptionDetailedCached` and `HediffDef.descriptionCached` are
    real private memoized fields that NO engine path ever clears. The staged
    lore mechanism nulls both by reflection; if Ludeon ever renames one, these
    cases fail instead of the feature silently serving last stage's text in
    every trade, transfer, storage-filter and hediff tooltip.
  * Each cache case primes the cache through the PUBLIC getter first, and there
    are two negative controls asserting a bare field write leaves the getter
    stale — without them the cache assertions would pass vacuously.
  * Reset-to-baseline: defs are process-global and are not reloaded between
    savegames, so the test applies a high stage, then a LOWER one, then zero,
    and demands the shipped strings back byte for byte.

dotnet is WINDOWS-NATIVE and cannot take a /mnt/d path, so this script finds
dotnet.exe and converts the repo-relative project path to a D-drive-style
path before invoking it.

    python3 selftest_lore_stages.py
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Utils -> RimMandrake -> src -> repo root.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CSPROJ = os.path.join(
    REPO, "src", "RimMandrake", "LoreStages", "Source", "SelfTest",
    "RimMandrakeLoreStages.SelfTest.csproj",
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
        sys.exit("RimMandrakeLoreStages.SelfTest.csproj not found at %s — the SelfTest "
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
