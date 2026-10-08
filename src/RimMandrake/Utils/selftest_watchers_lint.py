#!/usr/bin/env python3
"""Planted-defect selftest for lint_watchers_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_watchers_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selftest_modpack_lint as H  # noqa: E402

R = "Defs/ThingDefs_Races/RM_Piinnok.xml"
K = "Source/Kernel/RM_WatcherKernel.cs"
PLANTS = [
    ("flinch beyond watch", R, "<flinchRadius>6</flinchRadius>", "<flinchRadius>20</flinchRadius>", "wk-extension"),
    ("hide range reversed", R, "<hideTicks>2500~7500</hideTicks>", "<hideTicks>7500~2500</hideTicks>", "hideTicks"),
    ("wander chance above 1", R, "<wanderChance>0.1</wanderChance>", "<wanderChance>10</wanderChance>", "wanderChance"),
    ("hunger threshold above 1", R, "<emergeWhenFoodBelow>0.25</emergeWhenFoodBelow>", "<emergeWhenFoodBelow>2.5</emergeWhenFoodBelow>", "emergeWhenFoodBelow"),
    ("bolt time zero", R, "<boltTicks>1200</boltTicks>", "<boltTicks>0</boltTicks>", "boltTicks"),
    ("hediff undefined", R, "<hiddenHediff>RM_WatcherHidden</hiddenHediff>", "<hiddenHediff>RM_WatcherHiden</hiddenHediff>", "hiddenHediff"),
    ("sign undefined", R, "<signDef>RM_WatcherSign_SandDimple</signDef>", "<signDef>RM_WatcherSign_SandDimpl</signDef>", "signDef"),
    ("sign is the wrong class", "Defs/ThingDefs_Misc/RM_WatcherSigns.xml", "<thingClass>RimMandrake.Watchers.RM_WatcherSign</thingClass>", "<thingClass>Building</thingClass>", "RM_WatcherSign"),
    ("translation key missing", "Languages/English/Keyed/RM_Watchers.xml", "<RM_Watchers_Bolts>", "<RM_Watchers_Bolt>", "RM_Watchers_Bolts"),
    ("kernel imports Verse", K, "using System;", "using System;\nusing Verse;", "wk-kernel"),
    ("kernel missing from the csproj", "Source/RM_Watchers.csproj", '<Compile Include="Kernel\\RM_WatcherKernel.cs" />', "", "wk-kernel"),
    ("driver step interval hard-coded", "Source/RM_JobDriver_Watch.cs", "private const int StepInterval = RM_WatcherKernel.StepInterval;", "private const int StepInterval = 30;", "StepInterval"),
    ("literal recheck ticks", "Source/RM_JobGiver_WanderInMedium.cs", "TicksGame + RM_WatcherKernel.NoMediumRecheckTicks", "TicksGame + 7500", "7500"),
    ("orders patch names a missing designator", "Patches/RM_Watchers_OrdersDesignator.xml", "RM_Designator_Flush", "RM_Designator_Flushh", "wk-patch"),
    ("DefOf names a missing job", "Source/RM_WatchersDefOf.cs", "public static JobDef RM_WatcherFlush;", "public static JobDef RM_WatcherFlushh;", "DefOf"),
    ("job driver class typo", "Defs/JobDefs/RM_Watcher_Jobs.xml", "RM_JobDriver_Watch</driverClass>", "RM_JobDriver_Wach</driverClass>", "class-resolves"),
    ("settings Scribe default drifts", "Source/RM_WatchersMod.cs", '"maxActivePerMap", 40)', '"maxActivePerMap", 50)', "settings-scribed"),
]

if __name__ == "__main__":
    sys.exit(H.run("Watchers", "lint_watchers_defs.py", PLANTS, keep=("Languages",)))
