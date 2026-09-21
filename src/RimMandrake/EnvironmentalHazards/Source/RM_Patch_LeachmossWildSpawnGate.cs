using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // DESERT_LEACHMOSS_BUILD_1 — the settings toggle's mechanism.
    //
    // MEASURED against the decompiled 1.6 engine, 2026-09-20:
    // RimWorld/WildPlantSpawner.cs keeps its own per-MAP cache
    // (`cachedPlantCommonalities`, built once lazily from `map.Biomes` ->
    // `biome.wildPlants` and never invalidated) — so a Harmony patch on
    // `BiomeDef.CommonalityOfPlant` (a different, unrelated cache) would
    // not reach it, and there is no XML field to make wildPlants
    // conditional on a runtime Mod Settings bool. `CheckSpawnWildPlantAt`
    // — the single call site used for BOTH initial map-gen seeding and
    // every later regrowth roll (`PlantChoiceWeight` inside it is what
    // reads `plantRespawningCommonalityFactor`) — always starts by calling
    // `CalculatePlantsWhichCanGrowAt` to build the candidate list for the
    // cell, so a postfix there is the one choke point that covers both.
    //
    // Same shape as RimMandrake.StarWars.FireEcology.
    // Patch_EnforcePyrelandsWildPlantAllowlist (Pyrelands/Source/
    // WildPlantAllowlist.cs) — "the pattern the kit already uses to drop a
    // def from wildPlants" the item cites is that one; this is a denylist
    // of one defName rather than an allowlist, and unlike Pyrelands it is
    // not restricted to a single biome's maps, since RM_Leachmoss is not
    // listed in any other BiomeDef's wildPlants.
    [StaticConstructorOnStartup]
    public static class RM_LeachmossWildSpawnGatePatch
    {
        private const string LeachmossDefName = "RM_Leachmoss";

        static RM_LeachmossWildSpawnGatePatch()
        {
            var target = AccessTools.Method(typeof(WildPlantSpawner), "CalculatePlantsWhichCanGrowAt");
            if (target == null)
            {
                Log.Error("[RM EnvironmentalHazards] leachmoss-wild-spawn-gate: WildPlantSpawner."
                    + "CalculatePlantsWhichCanGrowAt not found — rule NOT armed. The engine signature "
                    + "this patch was written against has moved.");
                return;
            }

            try
            {
                Harmony harmony = new Harmony("mandrake.rm.environmentalhazards");
                harmony.Patch(target, postfix: new HarmonyMethod(
                    typeof(RM_LeachmossWildSpawnGatePatch), nameof(CalculatePlantsWhichCanGrowAt_Postfix)));
            }
            catch (Exception e)
            {
                Log.Error("[RM EnvironmentalHazards] leachmoss-wild-spawn-gate: patch failed, "
                    + "rule NOT armed. " + e);
            }
        }

        // outPlants is mutated in place by the original method; Harmony
        // hands a postfix the same List<ThingDef> reference, so removing
        // from it here is visible to the caller with no return-value dance.
        public static void CalculatePlantsWhichCanGrowAt_Postfix(List<ThingDef> outPlants)
        {
            if (RM_EnvironmentalHazardsSettings.leachmossEnabled)
            {
                return;
            }
            if (outPlants == null || outPlants.Count == 0)
            {
                return;
            }

            try
            {
                for (int i = outPlants.Count - 1; i >= 0; i--)
                {
                    if (outPlants[i]?.defName == LeachmossDefName)
                    {
                        outPlants.RemoveAt(i);
                    }
                }
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RM EnvironmentalHazards] leachmoss-wild-spawn-gate: " + e.Message, 0x4C4D31);
            }
        }
    }
}
