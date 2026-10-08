#!/usr/bin/env python3
"""Planted-defect selftest for lint_wreckedmachines_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_wreckedmachines_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selftest_modpack_lint as H  # noqa: E402

M = "Defs/ThingDefs_Buildings/Buildings_WreckedMachines_Mobile.xml"
T = "Defs/ThoughtDefs/Thoughts_WreckedMachines.xml"
K = "Source/Kernel/RM_WreckedMachinesKernel.cs"
S = "Source/WreckedMachinesMod.cs"
PLANTS = [
    ("unknown grade", M, "<grade>Kludged</grade>\n        <line>WM_PowerCell</line>", "<grade>Kludgd</grade>\n        <line>WM_PowerCell</line>", "unknown grade"),
    ("line missing", M, "<line>WM_PsychicEmanator</line>\n        <original>PsychicEmanator</original>\n        <emanates>true</emanates>", "<original>PsychicEmanator</original>\n        <emanates>true</emanates>", "no line"),
    ("replaceTags drift from the line", M, "<li>WM_PowerCell</li>", "<li>WM_PowerCel</li>", "replaceTags"),
    ("a rung duplicated", M, "<grade>Refurbished</grade>\n        <line>WM_PowerCell</line>", "<grade>Kludged</grade>\n        <line>WM_PowerCell</line>", "needs exactly one"),
    ("donor original disagrees within a line", M, "<original>VanometricPowerCell</original>", "<original>VanometricPowerCel</original>", "different donor originals"),
    ("kludged mood drifts from 5 x 0.2", T, "<baseMoodEffect>1</baseMoodEffect>", "<baseMoodEffect>2</baseMoodEffect>", "vanilla soothe"),
    ("refurbished mood drifts from 5 x 0.75", T, "<baseMoodEffect>3.75</baseMoodEffect>", "<baseMoodEffect>9</baseMoodEffect>", "vanilla soothe"),
    ("kernel imports Verse", K, "using System;", "using System;\nusing Verse;", "wm-kernel"),
    ("kernel missing from the csproj", "Source/RM_WreckedMachines.csproj", '<Compile Include="Kernel\\RM_WreckedMachinesKernel.cs" />', "", "wm-kernel"),
    ("slider tops out above the kernel cap", S, "list.Slider(refurbishedRatio, 0.3f, 0.95f)", "list.Slider(refurbishedRatio, 0.3f, 1.2f)", "tops out"),
    ("default outside its slider", S, "public static float kludgedRatio = 0.2f;", "public static float kludgedRatio = 0.7f;", "default"),
    ("hand copy of the material scaler", "Source/WreckedMachinesMod.cs", "RM_WreckedMachinesKernel.ScaledCount(entry.count, WreckedMachinesSettings.materialCostFactor)", "Mathf.RoundToInt(entry.count * WreckedMachinesSettings.materialCostFactor)", "material scaler"),
    ("settings Scribe default drifts", S, 'Scribe_Values.Look(ref refurbishedRatio, "refurbishedRatio", 0.75f, true)', 'Scribe_Values.Look(ref refurbishedRatio, "refurbishedRatio", 0.9f, true)', "settings-scribed"),
    ("class typo in a def extension", M, 'Class="RimMandrake.WreckedMachines.WreckedMachineGrade">\n        <grade>Wrecked</grade>', 'Class="RimMandrake.WreckedMachines.WreckedMachineGrad">\n        <grade>Wrecked</grade>', "class-resolves"),
]

if __name__ == "__main__":
    sys.exit(H.run("WreckedMachines", "lint_wreckedmachines_defs.py", PLANTS))
