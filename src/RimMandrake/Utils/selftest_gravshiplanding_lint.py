#!/usr/bin/env python3
"""Planted-defect selftest for lint_gravshiplanding_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_gravshiplanding_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modpack_lint_harness as H  # noqa: E402

M = "Source/GravshipLandingMod.cs"
P = "Source/Patch_GenStep_GravshipMarker.cs"
PLANTS = [
    ("harmony id differs from the packageId", M, 'HarmonyId = "mandrake.rm.gravshiplanding"', 'HarmonyId = "mandrake.rm.gravshiplandin"', "gl-harmony-id"),
    ("patch target changed", P, "nameof(GenStep_GravshipMarker.Generate)", "nameof(GenStep_GravshipMarker.GetHashCode)", "gl-patch-target"),
    ("postfix became a prefix", P, "[HarmonyPostfix]", "[HarmonyPrefix]", "gl-patch-target"),
    ("PatchAll removed", M, "new Harmony(HarmonyId).PatchAll(Assembly.GetExecutingAssembly());", "", "gl-patch-target"),
    ("postfix forgets the arrival flag", P, "RevealIfArrival(map, parms.gravship != null,", "RevealIfArrival(map, true,", "gl-gates-shared"),
    ("gate re-implemented outside the kernel", P, "RM_LandingKernel.Enabled(ModsConfig.OdysseyActive, arrival, GravshipLandingSettings.revealOutdoorsBeforeLanding)", "(ModsConfig.OdysseyActive && arrival)", "gl-gates-shared"),
    ("proof stops calling the shipped path", "Source/GravshipLandingProof.cs", "Patch_GenStep_GravshipMarker_Generate.RevealIfArrival(", "Patch_GenStep_GravshipMarker_Generate.RevealIfArrivalX(", "gl-gates-shared"),
    ("kernel imports Verse", "Source/Kernel/RM_LandingKernel.cs", "namespace RimMandrake.GravshipLanding", "using Verse;\nnamespace RimMandrake.GravshipLanding", "gl-kernel-pure"),
    ("kernel missing from the csproj", "Source/RM_GravshipLanding.csproj", '<Compile Include="Kernel\\RM_LandingKernel.cs" />', "", "compile-listed"),
    ("setting saved under another key", M, 'Scribe_Values.Look(ref revealOutdoorsBeforeLanding, "revealOutdoorsBeforeLanding", true)', 'Scribe_Values.Look(ref revealOutdoorsBeforeLanding, "reveal", true)', "settings-scribed"),
    ("setting default differs from the Scribe default", M, "public static bool revealOutdoorsBeforeLanding = true;", "public static bool revealOutdoorsBeforeLanding = false;", "settings-scribed"),
]

if __name__ == "__main__":
    sys.exit(H.run("GravshipLanding", "lint_gravshiplanding_defs.py", PLANTS, keep=("About",)))
