#!/usr/bin/env python3
"""Guard the exact vanilla constants two of MovingDunes' Harmony patches ride.

MOVING_DUNES_DESIGN.md §6 names this as the mod's own honourable-mention risk:

    "the two Harmony patches ride exact vanilla constants -- a game update silently
     changes dune behaviour; the loud-failure pattern plus one selftest asserting
     the constants is the guard."

This is that selftest. It reads the DECOMPILED RimWorld source and fails when a
constant the C# recognises by VALUE stops appearing there. A drift here does not
crash the game and does not log: the ambient-decay prefix simply stops matching, and
every dune on every map quietly evaporates over about five clear-weather days. That
is precisely the class of failure a test has to catch, because play never will.

Run:  python3 src/RimMandrake/MovingDunes/Source/selftest_moving_dunes_constants.py

If the decompiled source is not on this machine the test SKIPS loudly (exit 0 with a
SKIP line) rather than passing: an absent reference is ignorance, not a green light.
"""
import re
import sys
from pathlib import Path

# Not in the repo: the decompile is a large reference tree beside it.
DECOMPILED = Path("/mnt/d/Luke/dev/reference/rimworld-decompiled")

CSHARP = Path(__file__).resolve().parent

FAILURES = []
CHECKS = 0


def check(name, ok, detail):
    global CHECKS
    CHECKS += 1
    if ok:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}: {detail}")
        FAILURES.append(name)


def read(rel):
    p = DECOMPILED / rel
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8", errors="replace")


def main():
    if not DECOMPILED.is_dir():
        print(f"SKIP  decompiled RimWorld source not found at {DECOMPILED} — "
              "cannot verify the vanilla constants MovingDunes' patches ride. "
              "This is ignorance, not a pass.")
        return 0

    print("selftest_moving_dunes_constants")

    # ---- 1. the ambient sand decay the AddDepth prefix recognises by value -------
    steady = read("RimWorld/SteadyEnvironmentEffects.cs")
    if steady is None:
        print("SKIP  SteadyEnvironmentEffects.cs absent from the decompile.")
        return 0
    decay_calls = re.findall(r"sandGrid\.AddDepth\(\s*c\s*,\s*(-1f\s*/\s*180f)\s*\)", steady)
    check("ambient sand decay is still -1f/180f, in SteadyEnvironmentEffects",
          len(decay_calls) >= 1,
          "Patch_SandGrid_AddDepth matches that exact value and nothing else. "
          "If vanilla changed it, the suppression is inert and every dune "
          "evaporates in ~5 clear days with NO log line. Update "
          "MovingDunesMod.VanillaAmbientSandDecay to whatever it now is.")
    check("both decay sites (outdoor-clear and indoor) are still present",
          len(decay_calls) == 2,
          f"expected 2 call sites, found {len(decay_calls)}. A third would be a new "
          "decay path the prefix also catches (fine); ONE means a path was removed "
          "and the suppression now covers less than it claims.")

    # ---- 2. the sand-terrain exclusion the CanHaveSand prefix re-implements ------
    sandgrid = read("Verse/SandGrid.cs")
    if sandgrid is None:
        print("SKIP  SandGrid.cs absent from the decompile.")
        return 0
    check("SandGrid.CanHaveSand is still a private instance method taking an int",
          re.search(r"private\s+bool\s+CanHaveSand\s*\(\s*int\s+\w+\s*\)", sandgrid) is not None,
          "Patch_SandGrid_CanHaveSand targets exactly that signature via "
          "AccessTools.Method(typeof(SandGrid), \"CanHaveSand\", new[]{typeof(int)}). "
          "A changed signature arms nothing and logs TARGET METHOD NOT FOUND.")
    check("CanHaveSand still excludes Sand and SoftSand terrain",
          "TerrainDefOf.Sand" in sandgrid and "TerrainDefOf.SoftSand" in sandgrid,
          "The prefix exists ONLY to drop those two clauses. If vanilla stopped "
          "excluding sand terrain, the prefix is dead weight and should be deleted "
          "rather than left as an unexplained override.")
    check("CanHaveSand still honours holdSnowOrSand and the full-fillage edifice",
          "holdSnowOrSand" in sandgrid and "CanCoexistWithSand" in sandgrid,
          "The prefix re-implements both clauses. If either moved, water would take "
          "sand or walls would stop being free windbreaks.")
    check("SandGrid.MaxDepth is still 1.0",
          re.search(r"public\s+const\s+float\s+MaxDepth\s*=\s*1f\s*;", sandgrid) is not None,
          "Every tuning number in RM_DuneMaterialDef is expressed as a fraction of a "
          "1.0 cap. A different cap silently rescales the whole engine.")
    check("SandGrid's own mesh-dirty limiter is still 0.15 / 1.25%",
          "0.15f" in sandgrid and "0.0125f" in sandgrid,
          "slabSize = 0.05 is chosen to sit UNDER that limiter (design §6.1). If the "
          "limiter changed, transport starts dirtying a section per slab and the perf "
          "budget in the design no longer holds.")
    check("SandGrid.map is still the private field the patches read",
          re.search(r"private\s+Map\s+map\s*;", sandgrid) is not None,
          "SandGridAccess.MapOf uses AccessTools.FieldRefAccess<SandGrid, Map>(\"map\") "
          "to tell which map a grid belongs to. Without it BOTH sand rules go inert.")

    # ---- 3. the movement-category boundaries the hysteresis avoids ---------------
    buildup = read("Verse/WeatherBuildupUtility.cs")
    if buildup is None:
        print("SKIP  WeatherBuildupUtility.cs absent from the decompile.")
        return 0
    for boundary in ("0.03f", "0.25f", "0.5f", "0.75f"):
        check(f"buildup category boundary {boundary} still present",
              boundary in buildup,
              "MapComponent_DuneField.CategoryBoundaries lists these so deposition "
              "never rests a cell ON one. A stale list means path-cost recalc storms "
              "(design §6.2) come back, as a frame-rate bug nobody attributes here.")

    # ---- 4. the C# side still says what this test asserts ------------------------
    modcs = (CSHARP / "MovingDunesMod.cs").read_text(encoding="utf-8")
    check("MovingDunesMod still declares the decay constant as -1f/180f",
          "VanillaAmbientSandDecay = -1f / 180f" in modcs,
          "the C# and this test must name the same number, or the test guards nothing.")

    print(f"\n{CHECKS - len(FAILURES)}/{CHECKS} checks passed")
    if FAILURES:
        print("FAILED: " + ", ".join(FAILURES))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
