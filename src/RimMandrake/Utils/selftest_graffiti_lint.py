#!/usr/bin/env python3
"""Planted-defect selftest for lint_graffiti_defs.py: clean on the real mod and every mark in the repo, then one planted defect at a time.

    python3 src/RimMandrake/Utils/selftest_graffiti_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selftest_modpack_lint as H  # noqa: E402

D = "Defs/ThingDefs_Graffiti.xml"
G = "Defs/ThingDefs_GraffitiMemeGlyphs.xml"
M = "Source/RM_GraffitiMod.cs"
PLANTS = [
    ("form is not an enum name", D, "<form>Tag</form>", "<form>Tagg</form>", "gr-ext"),
    ("negative pool weight", D, "<poolWeight>", "<poolWeight>-", "gr-ext"),
    ("minArtistic far too high", D, "<minArtistic>6</minArtistic>", "<minArtistic>60</minArtistic>", "gr-ext"),
    ("thingClass back to plain Filth", D, "<thingClass>RimMandrake.Graffiti.Filth_Mark</thingClass>", "<thingClass>Filth</thingClass>", "gr-class"),
    ("category not Filth", D, "<category>Filth</category>", "<category>Item</category>", "gr-class"),
    ("slider wider than the kernel clamp", M, "list.Slider(paintIntervalTicks, 60f, 1000f)", "list.Slider(paintIntervalTicks, 0f, 1000f)", "gr-slider"),
    ("default outside the clamp", M, "public static int paintIntervalTicks = 250;", "public static int paintIntervalTicks = 5000;", "gr-slider"),
    ("kernel imports Verse", "Source/Kernel/RM_GraffitiKernel.cs", "using System;", "using System;\nusing Verse;", "gr-kernel-pure"),
    ("kernel missing from the csproj", "Source/Graffiti.csproj", '<Compile Include="Kernel\\RM_GraffitiKernel.cs" />', "", "compile-listed"),
    ("settings key differs", M, 'Scribe_Values.Look(ref breachBiasEnabled, "breachBiasEnabled", true)', 'Scribe_Values.Look(ref breachBiasEnabled, "breachBias", true)', "settings-scribed"),
]

if __name__ == "__main__":
    sys.exit(H.run("Graffiti", "lint_graffiti_defs.py", PLANTS))
