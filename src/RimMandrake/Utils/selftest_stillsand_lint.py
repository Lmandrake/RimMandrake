#!/usr/bin/env python3
"""Planted-defect selftest for lint_stillsand_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_stillsand_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modpack_lint_harness as H  # noqa: E402

I = "Defs/IncidentDefs/RM_SandLeviathanIncidents.xml"
W = "Defs/WeatherDefs/RM_DuneGale.xml"
T = "Defs/ThingDefs_Buildings/RM_Thumper.xml"
S = "Defs/ThingDefs_Buildings/RM_SolarStill.xml"
G = "Defs/ThingDefs_Buildings/RM_GlassChain_Buildings.xml"
PLANTS = [
    ("type typo in the leviathan extension Class=", I, 'Class="RimMandrake.Stillsand.RM_SandLeviathanExtension"', 'Class="RimMandrake.Stillsand.RM_SandLeviathanExtensio"', "class-resolves"),
    ("field typo under the leviathan extension", I, "<warningTicks>1500</warningTicks>", "<warningTick>1500</warningTick>", "fields-match"),
    ("muurrok pawnKind undefined", I, "<pawnKind>RM_Muurrok</pawnKind>", "<pawnKind>RM_Muurrk</pawnKind>", "stillsand-leviathan"),
    ("warning time zero", I, "<warningTicks>1500</warningTicks>", "<warningTicks>0</warningTicks>", "stillsand-leviathan"),
    ("vibration ceiling below 1 cuts the odds", I, "<beamCooldownTicks>600</beamCooldownTicks>", "<beamCooldownTicks>600</beamCooldownTicks><maxVibrationFactor>0.5</maxVibrationFactor>", "stillsand-leviathan"),
    ("biome list emptied", I, "<li>RM_Stillsand</li>", "", "stillsand-leviathan"),
    ("gale weather undefined", W, "<galeWeather>RM_DuneGale</galeWeather>", "<galeWeather>RM_DuneGal</galeWeather>", "stillsand-gale"),
    ("herald fraction above 1", W, "<heraldFraction>0.15</heraldFraction>", "<heraldFraction>1.5</heraldFraction>", "stillsand-gale"),
    ("return days reversed", W, "<returnDays>2~6</returnDays>", "<returnDays>6~2</returnDays>", "stillsand-gale"),
    ("alive chance above 1", W, "<returnAliveChance>0.75</returnAliveChance>", "<returnAliveChance>1.75</returnAliveChance>", "stillsand-gale"),
    ("emergence row that can never be chosen", W, "<weight>3</weight>", "<weight>0</weight>", "stillsand-gale"),
    ("duplicate emergence key", W, "<key>hull</key>", "<key>mummifiedCaravan</key>", "stillsand-gale"),
    ("emergence names an undefined mod thing", W, "<Cloth>40</Cloth>", "<RM_NoSuchCloth>40</RM_NoSuchCloth>", "stillsand-gale"),
    ("thumper never beats", T, "<beatIntervalTicks>600</beatIntervalTicks>", "<beatIntervalTicks>0</beatIntervalTicks>", "stillsand-sun"),
    ("thumper calls no one", T, "<maxCallsPerBeat>4</maxCallsPerBeat>", "<maxCallsPerBeat>0</maxCallsPerBeat>", "stillsand-sun"),
    ("still cycle of zero ticks", S, "<ticksPerCycle>6000</ticksPerCycle>", "<ticksPerCycle>0</ticksPerCycle>", "stillsand-sun"),
    ("still feed that yields nothing", S, "<litres>3</litres>", "<litres>0</litres>", "stillsand-sun"),
    ("sun factor floor above 1", G, "<minSunFactor>0.15</minSunFactor>", "<minSunFactor>1.5</minSunFactor>", "stillsand-sun"),
    ("unknown sun table kind", G, "<kind>lensBench</kind>", "<kind>lensBenc</kind>", "stillsand-sun"),
    ("settings key used twice", "Source/RM_DuneGaleSettings.cs", 'Scribe_Values.Look(ref galeEnabled, "galeEnabled", true);', 'Scribe_Values.Look(ref galeEnabled, "abrasionEnabled", true);', "stillsand-settings"),
    ("settings default differs from initialiser", "Source/RM_Thumper.cs", '"sw_thumperRadius", 40f)', '"sw_thumperRadius", 4f)', "stillsand-settings"),
    ("slider range excludes the default", "Source/RM_StillsandMod.cs", "list.Slider(thumperRadius, 10f, 80f)", "list.Slider(thumperRadius, 50f, 80f)", "stillsand-settings"),
    ("Scribe of a field the class does not declare", "Source/RM_Thumper.cs", 'Scribe_Values.Look(ref thumperRadius, "sw_thumperRadius", 40f);', 'Scribe_Values.Look(ref thumperRadiusX, "sw_thumperRadius", 40f);', "stillsand-settings"),
    ("a kernel file missing from the mod csproj", "Source/RM_Stillsand.csproj", '<Compile Include="Kernel\\RM_GaleKernel.cs" />', "", "compile-listed"),
    ("a kernel file missing from the fuzz project", "Source/SelfTest/Fuzz/RimMandrakeStillsand.Fuzz.csproj", '<Compile Include="..\\..\\Kernel\\RM_SunKernel.cs" />', "", "stillsand-kernel"),
    ("an engine reference inside a kernel", "Source/Kernel/RM_LedgerKernel.cs", "using System;\n", "using System;\nusing Verse;\n", "stillsand-kernel"),
]

if __name__ == "__main__":
    sys.exit(H.run("Stillsand", "lint_stillsand_defs.py", PLANTS))
