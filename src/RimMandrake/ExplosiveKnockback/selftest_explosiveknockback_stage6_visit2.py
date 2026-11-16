#!/usr/bin/env python3
"""Offline guards for the proof-scene faults Stage 6 visit 2 found live (2026-11-15,
design/concepts/ExplosiveKnockback/version/in_game/visit_2/SUMMARY.md). Read from the C# source, since the scenes only run
in a game:
  B1 SITE: a quicktest map's natural pond leaves FlowWorks a dry bed (bedGrid, depth 2 or 4) under the scene origin.
     Prepare paints the water to Soil but the bed stays, so the relative climb rule reads the takeoff cell at depth 4 and a
     colonist thrown into a depth-5 pit drops one notch: no descent (sc_pit_fall FAIL descents=0 at origin 12,12 on a
     BorealForest map; the same scene at a clean origin passed). Origins skips a candidate whose scene rect holds natural
     water, a lakebed or a natural bed (FlowWorks' IsNaturalBed), and Stage refuses INVALID when any cell of the prepared
     rect still reads a FlowWorks climb depth.
  G1 HARNESS: gas_into_pit_off lights the same cloud with the gas chain unhooked; vanilla fire then sets the colonist
     alight and a burning colonist runs (live: "Burning (fire size 31)", "Moving.", 4 to 9 cells, 2 of 4 runs). The
     control still refuses any burst, launch, descent or pit; it allows cells moved only when the colonist burned, and
     reports burned and cells.

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_stage6_visit2.py [--src DIR]
--src reads the mod's Source/ from DIR (laid out like this folder).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
fails = []


def check(code, ok, what):
    print("%s %s %s" % ("PASS" if ok else "FAIL", code, what))
    if not ok:
        fails.append(code)


def method(src, signature):
    """The body of the first method whose declaration contains `signature`, to its closing brace at that indent."""
    i = src.find(signature)
    if i < 0:
        return ""
    m = re.compile(r"\n        \}\n").search(src, i)
    return src[i:m.end()] if m else src[i:]


def main():
    root = sys.argv[sys.argv.index("--src") + 1] if "--src" in sys.argv else HERE
    src = os.path.join(root, "Source")
    proof = open(os.path.join(src, "RM_KnockbackProof.cs"), encoding="utf-8").read()
    compat = open(os.path.join(src, "RM_KnockbackCompat.cs"), encoding="utf-8").read()
    origins = method(proof, "public static string Origins(")
    if "PondSite(" in origins:
        origins += method(proof, "private static bool PondSite(")
    stage = method(proof, "public static string Stage(")
    check("B1a", '"ClimbDepthAt"' in compat and '"IsNaturalBed"' in compat,
          "compat resolves FlowWorks' ClimbDepthAt and IsNaturalBed by name")
    check("B1b", "public static int ClimbDepthAt(Map" in compat and "public static bool NaturalBedAt(Map" in compat,
          "compat exposes ClimbDepthAt(map, c) and NaturalBedAt(map, c)")
    check("B1c", "NaturalBedAt(" in origins and "IsWater" in origins and "RM_Lakebed" in origins,
          "Origins skips a scene rect with natural water, a lakebed or a natural bed")
    prep = stage.find("Prepare(s.o")
    after = stage[prep:] if prep >= 0 else ""
    check("B1d", prep >= 0 and "ClimbDepthAt(" in after and "INVALID" in after[:after.find("Build(s)")] if "Build(s)" in after
          else False, "Stage reads every prepared cell's climb depth and refuses INVALID before Build")
    i = proof.find('if (sc.name == "gas_into_pit_off")')
    off = proof[i:i + 900] if i >= 0 else ""
    ret = off[off.find("return Result("):off.find(";", off.find("return Result("))] if "return Result(" in off else ""
    check("G1", "burned" in off and "cells == 0 || burned" in ret and "launch.Count == 0" in ret and "!inPit" in ret
          and "desc.Count == 0" in ret and "bursts == 0" in ret,
          "gas_into_pit_off allows a fire run (burned) but still refuses burst, launch, descent and pit")
    print("explosiveknockback stage6 visit2: %d failed" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
