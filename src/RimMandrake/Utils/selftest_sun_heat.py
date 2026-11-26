#!/usr/bin/env python3
"""Wrapper for the C# selftest of Direct Sun (SOLAR_HEAT_EXPOSURE_1, DIRECT_SUN_SELFTEST_BUILD_EVERY_BIOME_EQUAL;
src/RimMandrake/CreatureBehaviors/Source/RM_SunHeatMath.cs).
Covers Direct Sun as a pure function of geometry: 55 x sin E, shadows h / tan E long, roofs, tents and parasols covering
at every E, the model taking no biome input, against vanilla's own HediffGiver_Heat curve; plus the body-size term, the
per-cell sun path cost, the directional shadow cast and the other Creature Behaviors sun kernels. See
CreatureBehaviors/Source/SelfTest/Program.cs's header for what is and is not covered and why. The defs half (no BiomeDef
carries a sun field) is selftest_direct_sun.py.

dotnet is WINDOWS-NATIVE and cannot take a /mnt/d path, so this script stages the project on D: first. It stages only
the folders the test reads (READS below), not the whole src tree: the whole tree cost 13m52s on 2026-11-26.

    python3 selftest_sun_heat.py [--require "<case name>" ...]
--require: exit 1 at once, without building, when a named case is not written in Program.cs; after the run, exit 1
unless each named case printed PASS. An outcome check names the cases its item owes.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
from selftest_winstage import windows_project_path
from winbuild import run_interop_captured
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Utils -> RimMandrake -> src -> repo root.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CSPROJ = os.path.join(
    REPO, "src", "RimMandrake", "CreatureBehaviors", "Source", "SelfTest",
    "RimMandrakeCreatureBehaviors.SunHeat.SelfTest.csproj",
)
PROGRAM = os.path.join(os.path.dirname(CSPROJ), "Program.cs")
# Every folder Program.cs reads a shipped file from (FindModsRoot() and root/".."); the csproj's own sources are staged
# by winbuild from the csproj. A new read outside these fails the run with a missing-file exception, never silently.
READS = [os.path.join(REPO, "src", "RimMandrake", m) for m in
         ("CreatureBehaviors", "EnvironmentalHazards", "LongShade", "Stillsand", "MovingDunes")] + \
        [os.path.join(REPO, "src", "RimStarWars", m) for m in ("SWBestiary", "StarWarsRaces")]

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


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--require", action="append", default=[], help="a case name that must be written and PASS")
    a = ap.parse_args(argv)
    if a.require:
        with open(PROGRAM, encoding="utf-8") as f:
            prog = f.read()
        missing = [r for r in a.require if ('"' + r + '"') not in prog]
        if missing:
            print("FAIL required case(s) not written in Program.cs: %s" % "; ".join(missing))
            sys.exit(1)
    if not os.path.isfile(CSPROJ):
        sys.exit("SunHeat SelfTest csproj not found at %s — the SelfTest "
                 "project moved or was never built" % CSPROJ)
    dotnet = _find_dotnet()
    if dotnet is None:
        sys.exit(
            "dotnet.exe not found at any of %r — this selftest needs the "
            "user-local Windows-side .NET SDK (see CLAUDE.md's C# build "
            "toolchain note); UNMEASURED, not a pass or a fail" % DOTNET_CANDIDATES)
    win_csproj = windows_project_path(CSPROJ, whole_src=False, extra_dirs=READS)
    cmd = [dotnet, "run", "--project", win_csproj, "-c", "Release"]
    r = run_interop_captured(cmd, stdout=subprocess.PIPE, text=True, errors="replace", timeout=900)
    out = r.stdout or ""
    sys.stdout.write(out)
    sys.stdout.flush()
    if r.stderr:
        sys.stderr.write(r.stderr)
    if r.returncode:
        sys.exit(r.returncode)
    passed = set(re.findall(r"^PASS (.*)$", out, re.M))
    unproven = [x for x in a.require if x not in passed]
    if unproven:
        print("FAIL required case(s) did not PASS: %s" % "; ".join(unproven))
        sys.exit(1)
    if not re.search(r"^(\d+)/\1 passed$", out, re.M):
        print("COULD NOT LOOK: no 'N/N passed' verdict line in the selftest output")
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
