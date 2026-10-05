#!/usr/bin/env python3
"""Wrapper for the C# selftest of the half-buried-in-sand graphic (LONGSHADE_SHEET_STRUCTURAL_RULINGS_1,
src/RimMandrake/CreatureBehaviors/Source/RM_SandBuriedGraphicDecision.cs).
Same shape as selftest_track_grid.py. Two halves:
  1. DEF WIRING (python, offline): every race ThingDef carrying RM_SandBuriedGraphicExtension has a
     PawnKindDef whose EVERY life stage declares swimmingGraphicData — the postfix draws that slot,
     and a missing one would silently draw nothing different. Sanity probe: RM_Drazzik must be found,
     so a parser that finds nothing fails instead of passing.
  2. THE DECISION (C#, dotnet): CreatureBehaviors/Source/SelfTestSandBuried/Program.cs — named owner
     cases plus all 256 input combinations. What neither half covers (the Harmony postfix landing, the
     look of the art) is the live half.

dotnet is WINDOWS-NATIVE and cannot take a /mnt/d path, so this script finds
dotnet.exe and converts the project path to a D-drive-style path first.

    python3 selftest_sand_buried_graphic.py
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Utils -> RimMandrake -> src -> repo root.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CSPROJ = os.path.join(
    REPO, "src", "RimMandrake", "CreatureBehaviors", "Source", "SelfTestSandBuried",
    "RimMandrakeCreatureBehaviors.SandBuried.SelfTest.csproj",
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


def check_def_wiring():
    import glob
    import xml.etree.ElementTree as ET
    ext_races, kinds = set(), {}
    for f in glob.glob(os.path.join(REPO, "src", "**", "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for td in root.iter("ThingDef"):
            for li in td.findall("modExtensions/li"):
                if (li.get("Class") or "").endswith("RM_SandBuriedGraphicExtension"):
                    ext_races.add(td.findtext("defName"))
        for pk in root.iter("PawnKindDef"):
            race = pk.findtext("race")
            if race:
                kinds.setdefault(race, []).append(pk)
    fails = 0
    if "RM_Drazzik" not in ext_races:
        print("FAIL  sanity probe: RM_Drazzik carries RM_SandBuriedGraphicExtension (found %d races)" % len(ext_races))
        fails += 1
    for race in sorted(ext_races):
        stages = [li for pk in kinds.get(race, []) for li in pk.findall("lifeStages/li")]
        missing = [i for i, li in enumerate(stages) if li.find("swimmingGraphicData/texPath") is None]
        if not stages or missing:
            print("FAIL  %s: life stages without swimmingGraphicData: %s" % (race, missing or "no PawnKindDef"))
            fails += 1
        else:
            print("PASS  %s: %d life stages carry swimmingGraphicData" % (race, len(stages)))
    return fails


def main():
    if check_def_wiring():
        sys.exit(1)
    if not os.path.isfile(CSPROJ):
        sys.exit("SandBuried.SelfTest.csproj not found at %s — the SelfTest "
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
