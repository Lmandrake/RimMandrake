#!/usr/bin/env python3
"""Planted-defect selftest for lint_pyrelands_defs.py: clean on the real mod, then one planted defect at a time is caught.
(The companion mandrake.rut.pyrelandsmechanics is read from the repo, not from the copy, so its own defects are covered by the
parser sanity checks in the lint rather than by planting.)

    python3 src/RimMandrake/Utils/selftest_pyrelands_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modpack_lint_harness as H  # noqa: E402

B = "Defs/BiomeDefs/Pyrelands.xml"
U = "Source/PyrelandsTuning.cs"
PLANTS = [
    ("raid threshold above the arson-debt cap", U, "ArsonDebtRaidThreshold = 400f", "ArsonDebtRaidThreshold = 4000f", "pyrelands-tuning"),
    ("fire-front days reversed", U, "FireFrontMinDays = 2f", "FireFrontMinDays = 9f", "pyrelands-tuning"),
    ("charge hysteresis crossed", U, "FurnaceChargeSeekBelow = 0.75f", "FurnaceChargeSeekBelow = 0.99f", "pyrelands-tuning"),
    ("no dead band between bleed and charge", U, "FurnaceBleedAmbientC = 5f", "FurnaceBleedAmbientC = 50f", "pyrelands-tuning"),
    ("reseed retry longer than the quiet time", U, "StandingBurnRetryTicks = 2500", "StandingBurnRetryTicks = 999999", "pyrelands-tuning"),
    ("a biome on two herd legs", U, '"Desert", "RUT_Desert"', '"Desert", "ZBiome_Grasslands", "RUT_Desert"', "pyrelands-tuning"),
    ("class typo in a think tree", "Defs/ThinkTreeDefs/RM_BurrowOnFireThinkTree.xml", 'Class="RimMandrake.Pyrelands.RM_JobGiver_BurrowOnFire"', 'Class="RimMandrake.Pyrelands.RM_JobGiver_BurrowOnFir"', "class-resolves"),
    ("biome worker class typo", B, "RimMandrake.Pyrelands.BiomeWorker_Pyrelands</workerClass>", "RimMandrake.Pyrelands.BiomeWorker_Pyrelandz</workerClass>", "pyrelands-biome"),
    ("rainfall band reversed", B, "<rainfall>550~1000</rainfall>", "<rainfall>1000~550</rainfall>", "pyrelands-biome"),
    ("score never beats arid shrubland", B, "<baseScore>30</baseScore>", "<baseScore>1</baseScore>", "pyrelands-biome"),
    ("plant density differs from the enforcer", B, "<plantDensity>16</plantDensity>", "<plantDensity>3</plantDensity>", "pyrelands-biome"),
    ("regrow days differ from the enforcer", B, "<wildPlantRegrowDays>9</wildPlantRegrowDays>", "<wildPlantRegrowDays>20</wildPlantRegrowDays>", "pyrelands-biome"),
    ("wild plant row not on the allowlist", B, "<RM_FE_Plant_Quickgrass>3.8</RM_FE_Plant_Quickgrass>", "<RM_FE_Plant_Quickgrass>3.8</RM_FE_Plant_Quickgrass><RM_FE_Plant_Other>1</RM_FE_Plant_Other>", "pyrelands-biome"),
    ("allowlisted plant undefined", "Source/WildPlantAllowlist.cs", '"RM_FE_Plant_Quickgrass",', '"RM_FE_Plant_Quickgras",', "pyrelands-biome"),
    ("settings key differs from field", "Source/RM_PyrelandsMod.cs", 'Scribe_Values.Look(ref ashfallRateMultiplier, "ashfallRateMultiplier", 1f);', 'Scribe_Values.Look(ref ashfallRateMultiplier, "ashRate", 1f);', "settings-scribed"),
    ("settings default differs from initialiser", "Source/RM_PyrelandsMod.cs", '"ashfallRateMultiplier", 1f)', '"ashfallRateMultiplier", 2f)', "settings-scribed"),
    ("slider range excludes the default", "Source/RM_PyrelandsMod.cs", "list.Slider(ashfallRateMultiplier, 0.25f, 3f)", "list.Slider(ashfallRateMultiplier, 1.5f, 3f)", "settings-range"),
    ("a kernel file missing from the mod csproj", "Source/FireEcologyHook.csproj", '<Compile Include="Kernel\\RM_BreakerKernel.cs" />', "", "compile-listed"),
    ("a kernel file missing from the fuzz project", "Source/SelfTest/Fuzz/RimMandrakePyrelands.Fuzz.csproj", '<Compile Include="..\\..\\Kernel\\RM_FireEcoKernel.cs" />', "", "pyrelands-kernel"),
    ("FurnaceWarmthMath missing from the fuzz project", "Source/SelfTest/Fuzz/RimMandrakePyrelands.Fuzz.csproj", '<Compile Include="..\\..\\FurnaceWarmthMath.cs" />', "", "pyrelands-kernel"),
    ("an engine reference inside a kernel", "Source/Kernel/RM_FireEcoKernel.cs", "using System;\n", "using System;\nusing Verse;\n", "pyrelands-kernel"),
    ("burn-history constant changed under the fuzz", "Source/MapComponent_BurnLine.cs", "BurnHistoryIntervalTicks = 2500", "BurnHistoryIntervalTicks = 3000", "pyrelands-kernel"),
]

if __name__ == "__main__":
    sys.exit(H.run("Pyrelands", "lint_pyrelands_defs.py", PLANTS))
