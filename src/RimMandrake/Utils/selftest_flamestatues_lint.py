#!/usr/bin/env python3
"""Planted-defect selftest for lint_flamestatues_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_flamestatues_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modpack_lint_harness as H  # noqa: E402

D = "Defs/ThingDefs_Buildings/RM_FlameStatues.xml"
PLANTS = [
    ("a vent dropped from the dancer", D, "          <li><offset>(-0.30,0,0.63)</offset><size>0.35</size></li>   <!-- left palm -->\n", "", "fs-points"),
    ("a vent outside the sprite", D, "<offset>(0,0,0.5)</offset>", "<offset>(0,0,4.5)</offset>", "fs-points"),
    ("a vent of size zero", D, "<offset>(0,0,0.5)</offset><size>0.35</size>", "<offset>(0,0,0.5)</offset><size>0</size>", "fs-points"),
    ("ticker no longer Normal", D, "<tickerType>Normal</tickerType>", "<tickerType>Rare</tickerType>", "fs-ticker"),
    ("drawer type lost", D, "<drawerType>MapMeshAndRealTime</drawerType>", "<drawerType>MapMeshOnly</drawerType>", "fs-ticker"),
    ("wood allowed as fuel", D, "<fuelFilter><thingDefs><li>Chemfuel</li></thingDefs></fuelFilter>", "<fuelFilter><thingDefs><li>WoodLog</li></thingDefs></fuelFilter>", "fs-fuel"),
    ("fuel target above capacity", D, "<initialConfigurableTargetFuelLevel>5</initialConfigurableTargetFuelLevel>", "<initialConfigurableTargetFuelLevel>50</initialConfigurableTargetFuelLevel>", "fs-fuel"),
    ("auto refuel above 1", D, "<autoRefuelPercent>0.35</autoRefuelPercent>", "<autoRefuelPercent>1.5</autoRefuelPercent>", "fs-fuel"),
    ("glow colour channel above 255", D, "<glowRadius>4</glowRadius>\n        <glowColor>(255,120,40,0)</glowColor>", "<glowRadius>4</glowRadius>\n        <glowColor>(255,320,40,0)</glowColor>", "fs-fuel"),
    ("ember out-burns the dancer", D, "<fuelConsumptionRate>0.12</fuelConsumptionRate>", "<fuelConsumptionRate>0.9</fuelConsumptionRate>", "fs-ladder"),
    ("fleck interval 74 puffs in unison", D, "<size>0.55</size></li>   <!-- crown -->\n        </points>\n        <qualityScalingEnabled>true</qualityScalingEnabled>\n        <fireGlowFleckIntervalTicks>90</fireGlowFleckIntervalTicks>", "<size>0.55</size></li>   <!-- crown -->\n        </points>\n        <qualityScalingEnabled>true</qualityScalingEnabled>\n        <fireGlowFleckIntervalTicks>74</fireGlowFleckIntervalTicks>", "fs-phase"),
    ("slider wider than the kernel clamp", "Source/FlameStatuesMod.cs", "list.Slider(consumptionMultiplier, 0.25f, 4f)", "list.Slider(consumptionMultiplier, 0.25f, 8f)", "fs-slider"),
    ("multiplier default not 1", "Source/FlameStatuesMod.cs", "public static float consumptionMultiplier = 1f;", "public static float consumptionMultiplier = 2f;", "fs-slider"),
    ("kernel imports Unity", "Source/Kernel/RM_FlameKernel.cs", "using System;", "using System;\nusing UnityEngine;", "fs-kernel-pure"),
    ("kernel missing from the csproj", "Source/RimMandrake.FlameStatues.csproj", '<Compile Include="Kernel\\RM_FlameKernel.cs" />', "", "compile-listed"),
    ("settings key differs", "Source/FlameStatuesMod.cs", 'Scribe_Values.Look(ref glow, "glow", true)', 'Scribe_Values.Look(ref glow, "glo", true)', "settings-scribed"),
]

if __name__ == "__main__":
    sys.exit(H.run("FlameStatues", "lint_flamestatues_defs.py", PLANTS))
