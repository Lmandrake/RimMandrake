#!/usr/bin/env python3
"""Planted-defect selftest for lint_explosiveknockback_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_explosiveknockback_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modpack_lint_harness as H  # noqa: E402

P = "Patches/RM_Knockback_DamageDefs.xml"
F = "Defs/ThingDefs/RM_PawnFlyer_Knockback.xml"
M = "Source/RM_KnockbackMod.cs"
PLANTS = [
    ("extension field typo", P, "<force>1.0</force>", "<forse>1.0</forse>", "ek-ext"),
    ("negative force", P, "<force>1.0</force>", "<force>-1</force>", "ek-ext"),
    ("force far too large", P, "<force>1.0</force>", "<force>50</force>", "ek-ext"),
    ("patch targets a damage def nobody defines", P, 'DamageDef[defName="Smoke"]', 'DamageDef[defName="Smok"]', "ek-ext"),
    ("flyer thingClass changed", F, "<thingClass>PawnFlyer</thingClass>", "<thingClass>RimWorld.PawnFlyerX</thingClass>", "ek-flyer"),
    ("flyer parent changed", F, 'ParentName="PawnFlyerBase"', 'ParentName="PawnFlyerBasX"', "ek-flyer"),
    ("flyer speed zero", F, "<flightSpeed>12</flightSpeed>", "<flightSpeed>0</flightSpeed>", "ek-flyer"),
    ("flyer curve falls", F, "<li>(0.1, 0.2)</li>", "<li>(0.1, 1.5)</li>", "ek-flyer"),
    ("flyer stun inverted", F, "<stunDurationTicksRange>60~120</stunDurationTicksRange>", "<stunDurationTicksRange>120~60</stunDurationTicksRange>", "ek-flyer"),
    ("reset writes another default", M, "RimMandrakeExplosiveKnockbackSettings.strength = 1f;\n            RimMandrakeExplosiveKnockbackSettings.maxThrowCells = 6;", "RimMandrakeExplosiveKnockbackSettings.strength = 2f;\n            RimMandrakeExplosiveKnockbackSettings.maxThrowCells = 6;", "ek-reset"),
    ("reset forgets a setting", M, "            RimMandrakeExplosiveKnockbackSettings.shieldDebitPerForce = 10f;\n        }\n    }", "        }\n    }", "ek-reset"),
    ("slider excludes the default", M, "RimMandrakeExplosiveKnockbackSettings.immuneBodySize = l.Slider(RimMandrakeExplosiveKnockbackSettings.immuneBodySize, 1f, 5f)", "RimMandrakeExplosiveKnockbackSettings.immuneBodySize = l.Slider(RimMandrakeExplosiveKnockbackSettings.immuneBodySize, 3f, 5f)", "ek-reset"),
    ("kernel imports Verse", "Source/RM_KnockbackMath.cs", "using System;", "using System;\nusing Verse;", "ek-kernel"),
    ("harmony id differs", M, 'new Harmony("mandrake.rm.explosiveknockback")', 'new Harmony("mandrake.rm.explosiveknockbac")', "ek-kernel"),
    ("settings key differs", M, 'Scribe_Values.Look(ref strength, "strength", 1f)', 'Scribe_Values.Look(ref strength, "power", 1f)', "settings-scribed"),
    ("settings default differs", M, 'Scribe_Values.Look(ref maxThrowCells, "maxThrowCells", 6)', 'Scribe_Values.Look(ref maxThrowCells, "maxThrowCells", 7)', "settings-scribed"),
    ("source file missing from the csproj", "Source/RimMandrake_ExplosiveKnockback.csproj", '<Compile Include="RM_KnockbackCompat.cs" />', "", "compile-listed"),
]

if __name__ == "__main__":
    sys.exit(H.run("ExplosiveKnockback", "lint_explosiveknockback_defs.py", PLANTS, keep=("About",)))
