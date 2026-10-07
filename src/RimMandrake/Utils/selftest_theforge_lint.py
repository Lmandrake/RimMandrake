#!/usr/bin/env python3
"""Planted-defect selftest for lint_theforge_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_theforge_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selftest_modpack_lint as H  # noqa: E402

P = "Defs/GameConditionDefs/RM_ForgePulse.xml"
N = "Defs/ThingDefs_Races/RM_TheForgeNatives.xml"
PLANTS = [
    ("type typo in the cycle extension Class=", P, 'Class="RimMandrake.TheForge.RM_ForgeCycleExtension"', 'Class="RimMandrake.TheForge.RM_ForgeCycleExtensio"', "class-resolves"),
    ("field typo under the cycle extension", P, "<pumiceChance>0.3</pumiceChance>", "<pumiceChanse>0.3</pumiceChanse>", "fields-match"),
    ("phase range reversed", P, "<stillHours>48~72</stillHours>", "<stillHours>72~48</stillHours>", "theforge-cycle"),
    ("hiss lead longer than the still heat", P, "<hissLeadHours>1.5</hissLeadHours>", "<hissLeadHours>60</hissLeadHours>", "theforge-cycle"),
    ("pumice chance above 1", P, "<pumiceChance>0.3</pumiceChance>", "<pumiceChance>1.3</pumiceChance>", "theforge-cycle"),
    ("maxFrozenCells zero", P, "<maxFrozenCells>6000</maxFrozenCells>", "<maxFrozenCells>0</maxFrozenCells>", "theforge-cycle"),
    ("basalt terrain undefined", P, "<basaltTerrain>RM_BasaltShingle</basaltTerrain>", "<basaltTerrain>RM_BasaltShingel</basaltTerrain>", "theforge-cycle"),
    ("crust terrain not temporary", "Defs/TerrainDefs/RM_ForgeCycleTerrain.xml", "<temporary>true</temporary>", "<temporary>false</temporary>", "must be <temporary>"),
    ("garden cannot ripen in the shortest growth phase", P, "<growthHours>54~66</growthHours>", "<growthHours>10~66</growthHours>", "theforge-garden"),
    ("run clock without a slow hediff", N, "<slowHediff>RM_DhuvvoxRunSlowing</slowHediff>", "", "theforge-comps"),
    ("scuttle factor below 1", N, "<runSoundSlowFactor>4</runSoundSlowFactor>", "<runSoundSlowFactor>0.5</runSoundSlowFactor>", "theforge-comps"),
    ("empty stoop band", N, "<stoopMinDistance>8</stoopMinDistance>", "<stoopMinDistance>40</stoopMinDistance>", "theforge-comps"),
    ("settings key differs from field", "Source/RM_TheForgeMod.cs", 'Scribe_Values.Look(ref plumeStrength, "plumeStrength"', 'Scribe_Values.Look(ref plumeStrength, "plumeStr"', "settings-scribed"),
    ("settings default differs from initialiser", "Source/RM_TheForgeMod.cs", '"dhokkurTrailFadeDays", 60f)', '"dhokkurTrailFadeDays", 6f)', "settings-scribed"),
    ("slider range excludes the default", "Source/RM_TheForgeMod.cs", "list.Slider(dhokkurTrailFadeDays, 5f, 240f)", "list.Slider(dhokkurTrailFadeDays, 90f, 240f)", "settings-range"),
    ("a kernel file missing from the csproj", "Source/RM_TheForge.csproj", '<Compile Include="Kernel\\RM_CycleKernel.cs" />', "", "compile-listed"),
]

if __name__ == "__main__":
    sys.exit(H.run("TheForge", "lint_theforge_defs.py", PLANTS))
