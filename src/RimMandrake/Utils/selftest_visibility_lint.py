#!/usr/bin/env python3
"""Planted-defect selftest for lint_visibility_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_visibility_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modpack_lint_harness as H  # noqa: E402

K = "Source/Kernel/RM_VisibilityKernel.cs"
S = "Source/RM_VisibilityMod.cs"
G = "Source/GameComponent_ColonyVisibility.cs"
PLANTS = [
    ("kernel imports Verse", K, "using System;", "using System;\nusing Verse;", "vis-kernel"),
    ("season length drifts", K, "TicksPerSeason = 900000;", "TicksPerSeason = 840000;", "TicksPerSeason"),
    ("launch floor drifts", K, "LaunchFloor = 5f", "LaunchFloor = 0f", "launch floor/ceiling"),
    ("settings text loses the floor", S, "floor 5, ceiling 15", "floor 0, ceiling 15", "settings text"),
    ("curve nodes out of order", K, "CurveX = { 0f, 25f, 50f, 75f, 100f }", "CurveX = { 0f, 25f, 20f, 75f, 100f }", "threat curve nodes"),
    ("curve y falls", K, "CurveY = { 0.55f, 0.80f, 1.00f, 1.25f, 1.60f }", "CurveY = { 0.55f, 0.80f, 0.70f, 1.25f, 1.60f }", "threat curve nodes"),
    ("curve low point can zero a raid", K, "CurveY = { 0.55f,", "CurveY = { 0.45f,", "drives the factor"),
    ("strength slider past 2x", S, "list.Slider(raidScalingStrength, 0f, 2f)", "list.Slider(raidScalingStrength, 0f, 4f)", "strength slider"),
    ("mod stops calling the kernel band", G, "RM_VisibilityKernel.BandFor(v)", "(int)(v / 20f)", "BandFor"),
    ("hand copy of the dial clamp", G, "RM_VisibilityKernel.Adjust(shipVisibility, delta)", "Mathf.Clamp(shipVisibility + delta, 0f, 100f)", "hand copy of the dial clamp"),
    ("hand copy of the point clamp", "Source/ColonyVisibilityRaidPatch.cs", "RM_VisibilityKernel.ScalePoints(parms.points, factor, StorytellerUtility.GlobalPointsMin())", "Mathf.Clamp(parms.points * factor, StorytellerUtility.GlobalPointsMin(), 10000f)", "hand copy of the point clamp"),
    ("SelfTest leaks into the mod assembly", "Source/Visibility.csproj", '<Compile Remove="SelfTest/**/*.cs" />', "", "SelfTest"),
    ("settings Scribe default drifts", S, 'Scribe_Values.Look(ref launchResetMultiplier, "launchResetMultiplier", 0.15f)', 'Scribe_Values.Look(ref launchResetMultiplier, "launchResetMultiplier", 0.3f)', "settings-scribed"),
    ("settings key differs from field", S, '"raidScalingStrength", 1f)', '"strength", 1f)', "settings-scribed"),
    ("packageId drifts", "About/About.xml", "<packageId>mandrake.rm.visibility</packageId>", "<packageId>mandrake.rm.visiblity</packageId>", "vis-about"),
]

if __name__ == "__main__":
    sys.exit(H.run("Visibility", "lint_visibility_defs.py", PLANTS, keep=("About",)))
