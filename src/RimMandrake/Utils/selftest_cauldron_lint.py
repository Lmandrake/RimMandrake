#!/usr/bin/env python3
"""Planted-defect selftest for lint_cauldron_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_cauldron_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modpack_lint_harness as H  # noqa: E402

V = "Defs/ThingDefs_Buildings/RM_CauldronVent.xml"
F = "Defs/ThingDefs_Plants/RM_CauldronFlora.xml"
A = "Defs/ThingDefs_Races/RM_CauldronFauna.xml"
M = "Source/RM_CauldronMod.cs"
PLANTS = [
    ("type typo in the vent extension Class=", V, 'Class="RimMandrake.Cauldron.RM_VentExtension"', 'Class="RimMandrake.Cauldron.RM_VentExtensio"', "class-resolves"),
    ("field typo under the vent extension", V, "<falterOutput>0.1</falterOutput>", "<falterOutpu>0.1</falterOutpu>", "fields-match"),
    ("bloom weather undefined", V, "<bloomWeather>RM_VentBloom</bloomWeather>", "<bloomWeather>RM_VentBlom</bloomWeather>", "cauldron-vent"),
    ("falter louder than the rows", V, "<falterOutput>0.1</falterOutput>", "<falterOutput>3</falterOutput>", "cauldron-vent"),
    ("bloom row quieter than the default", V, "<weather>RM_VentBloom</weather><output>2.5</output>", "<weather>RM_VentBloom</weather><output>0.5</output>", "cauldron-vent"),
    ("a weather listed twice", V, "<weather>RM_Dewfall</weather>", "<weather>RM_VapourBank</weather>", "cauldron-vent"),
    ("recover time zero", V, "<recoverTicks>60000</recoverTicks>", "<recoverTicks>0</recoverTicks>", "cauldron-vent"),
    ("garden chance above 1", F, "<mapgenChance>0.3</mapgenChance>", "<mapgenChance>1.3</mapgenChance>", "cauldron-garden"),
    ("vent ring reversed", F, "<ventRadius>7</ventRadius>", "<ventRadius>2</ventRadius>", "cauldron-garden"),
    ("unknown vent habitat", F, "<ventHabitat>StableRing</ventHabitat>", "<ventHabitat>StableRng</ventHabitat>", "cauldron-garden"),
    ("more metal at minimum growth than at full", F, "<countAtFullGrowth>12</countAtFullGrowth>", "<countAtFullGrowth>1</countAtFullGrowth>", "cauldron-yield"),
    ("fleck bands reversed", F, "<lightTexPath>Things/Plant/RM_AssayFlecks/Flecks_Light</lightTexPath>", "<lightTexPath>Things/Plant/RM_AssayFlecks/Flecks_Light</lightTexPath><lightFrom>0.9</lightFrom>", "cauldron-flecks"),
    ("vexxiss interval zero", A, "<waterPoisonRadius>1.5</waterPoisonRadius>", "<waterPoisonRadius>1.5</waterPoisonRadius><ventScanIntervalTicks>0</ventScanIntervalTicks>", "cauldron-vexxiss"),
    ("a water swap that changes nothing", A, "<from>WaterShallow</from><to>ToxicWaterShallow</to>", "<from>WaterShallow</from><to>WaterShallow</to>", "cauldron-vexxiss"),
    ("settings key differs from field", M, 'Scribe_Values.Look(ref ventSilenceDays, "ventSilenceDays"', 'Scribe_Values.Look(ref ventSilenceDays, "ventSilence"', "settings-scribed"),
    ("settings default differs from initialiser", M, 'Scribe_Values.Look(ref ventSilenceDays, "ventSilenceDays", 4f, true)', 'Scribe_Values.Look(ref ventSilenceDays, "ventSilenceDays", 5f, true)', "settings-scribed"),
    ("slider range excludes the default", M, "list.Slider(ventSilenceDays, 1f, 10f)", "list.Slider(ventSilenceDays, 5f, 10f)", "settings-range"),
    ("a kernel file missing from the csproj", "Source/RM_Cauldron.csproj", '<Compile Include="Kernel\\RM_VentKernel.cs" />', "", "compile-listed"),
]

if __name__ == "__main__":
    sys.exit(H.run("Cauldron", "lint_cauldron_defs.py", PLANTS))
