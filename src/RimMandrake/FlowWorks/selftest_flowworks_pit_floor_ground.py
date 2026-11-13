#!/usr/bin/env python3
"""RIMMANDRAKE_ALLOW_MEDIUM_FURNITURE_ON_PIT_FLOOR: a dry dug floor carries what its ground carried.

Seen live 2026-11-12: a butcher table, tailoring bench, battery, cooler, RM_ResinSealingJarShelf and RM_BrineCrock were
refused on a 4 m dug floor ("requires terrain that supports Medium"): RM_Channel_Superdeep carries Light only.
Design (recorded in the item): a pit floor is solid ground a colony builds on; it carries the load-bearing affordances
(Light, Medium, Heavy) of the ground it was dug from (RM_MapComponent_Excavation.OriginalTerrainAt), through one postfix
on GridsUtility.GetAffordances, which GenConstruct.CanBuildOnTerrain reads per cell. Wet dug squares are vanilla water and
keep their own rule (buildInDugWaterEnabled). The numbers are the C# case PitFloorGround_dug_floor_carries_its_grounds_load
(selftest_flowworks_stock.py); this checks the wiring and the Mod Setting.

CAN IT FAIL: each wire taken out of a copy of the source must go red (run at the end).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "Source"
sys.path.insert(0, str(HERE))
from selftest_flowworks_underliquid_parity import mask_comments, method_body  # noqa: E402

PATCH = SRC / "Superdeep" / "RM_PitFloorGround.cs"
MATH = SRC / "Superdeep" / "RM_PitFloorGroundMath.cs"
FILES = {"patch": PATCH, "math": MATH, "mod": SRC / "RimMandrakeFlowWorksMod.cs",
         "csproj": SRC / "RimMandrake_FlowWorks.csproj", "stcsproj": SRC / "SelfTest" / "RimMandrakeFlowWorks.SelfTest.csproj",
         "program": SRC / "SelfTest" / "Program.cs"}


def checks(t: dict) -> list[tuple[str, bool]]:
    patch, math, mod = mask_comments(t["patch"]), mask_comments(t["math"]), t["mod"]
    post = method_body(patch, r"private static void Postfix\(IntVec3 c, Map map, ref List<TerrainAffordanceDef> __result\)")
    carried = method_body(math, r"public static List<T> Carried<T>\(List<T> floor, List<T> ground, Func<T, string> name\)")
    return [
        ("the math is Verse-free", bool(math) and "using Verse" not in math and "using RimWorld" not in math),
        ("Carried lends only Light, Medium and Heavy", bool(carried) and all(f'"{a}"' in math for a in ("Light", "Medium", "Heavy"))
         and "GrowSoil" not in math),
        ("the patch is a postfix on GridsUtility.GetAffordances",
         "[HarmonyPatch(typeof(GridsUtility), nameof(GridsUtility.GetAffordances))]" in patch and bool(post)),
        ("the postfix is gated by the setting", "RimMandrakeFlowWorksSettings.pitFloorCarriesGroundEnabled" in post),
        ("a foundation keeps vanilla's answer", "FoundationAt(c) != null" in post),
        ("a square under a suspension deck keeps the deck's tier", "RM_MapComponent_SuspensionBridges.DeckAt(map, c) != null" in post),
        ("only a dry dug floor (DepthOfDryTerrain) lends", "RM_ExcavationDepth.DepthOfDryTerrain(" in post),
        ("the ground is the terrain recorded before the first cut", "OriginalTerrainAt(c)" in post),
        ("the merged lists are cached, not rebuilt per call", "cache" in patch and "RM_PitFloorGroundMath.Carried(" in patch),
        ("Mod Setting: field, scribe, section and checkbox",
         "public static bool pitFloorCarriesGroundEnabled = true;" in mod
         and 'Scribe_Values.Look(ref pitFloorCarriesGroundEnabled, "pitFloorCarriesGroundEnabled", true);' in mod
         and '"pitFloorCarriesGroundEnabled"' in mod and "ref pitFloorCarriesGroundEnabled," in mod),
        ("both files are compiled", 'Include="Superdeep\\RM_PitFloorGround.cs"' in t["csproj"]
         and 'Include="Superdeep\\RM_PitFloorGroundMath.cs"' in t["csproj"]
         and 'Include="..\\Superdeep\\RM_PitFloorGroundMath.cs"' in t["stcsproj"] and 'Include="PitFloorGroundChecks.cs"' in t["stcsproj"]),
        ("the C# case runs", "PitFloorGroundChecks.Run(Case);" in t["program"]),
    ]


def run(rows) -> int:
    bad = 0
    for name, ok in rows:
        print(("PASS " if ok else "FAIL ") + name)
        bad += not ok
    return bad


def main() -> int:
    t = {k: (p.read_text(encoding="utf-8") if p.exists() else "") for k, p in FILES.items()}
    bad = run(checks(t))
    plants = [
        ("setting gate removed", "patch", "RimMandrakeFlowWorksSettings.pitFloorCarriesGroundEnabled", "true"),
        ("foundation check removed", "patch", "FoundationAt(c) != null", "false"),
        ("deck guard removed", "patch", "RM_MapComponent_SuspensionBridges.DeckAt(map, c) != null", "false"),
        ("GrowSoil lent", "math", '"Heavy"', '"Heavy", "GrowSoil"'),
        ("dry-floor check removed", "patch", "RM_ExcavationDepth.DepthOfDryTerrain(", "Ignored("),
        ("checkbox dropped", "mod", "ref pitFloorCarriesGroundEnabled,", "ref nothing,"),
    ]
    for name, key, old, new in plants:
        t2 = dict(t)
        t2[key] = t[key].replace(old, new)
        caught = any(not ok for _, ok in checks(t2))
        print(("PASS " if caught else "FAIL ") + "can-fail: " + name + " goes red")
        bad += not caught
    print("RESULT", "GREEN" if not bad else "RED %d" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
