using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // MIASMA_KARRATHIL_POLLINATION_GATE_1 — see RM_PollinationGateExtension.cs
    // for the full Desktop-verified engine rationale (WildPlantSpawner is the
    // sole reproduction authority; no Plant-level comp hook exists; this
    // choke point is the same private method RM_LeachmossWildSpawnGatePatch
    // already proves patchable). This patch reads the data-driven extension
    // instead of that sibling's single hardcoded defName.
    //
    // Needs the WildPlantSpawner's owning Map to check pollinator presence,
    // which the class keeps as a private field — same
    // AccessTools.FieldRefAccess reflection shape this repo already uses for
    // exactly this problem on a different private-map class (RimMandrake.
    // MovingDunes.Source.Patch_SandGrid's SandGridAccess).
    [StaticConstructorOnStartup]
    public static class RM_PollinationGatePatch
    {
        private static AccessTools.FieldRef<WildPlantSpawner, Map> mapRef;

        static RM_PollinationGatePatch()
        {
            try
            {
                mapRef = AccessTools.FieldRefAccess<WildPlantSpawner, Map>("map");
            }
            catch (Exception e)
            {
                Log.Error("[RM EnvironmentalHazards] pollination-gate: WildPlantSpawner.map field "
                    + "not found — rule NOT armed. " + e.Message);
                return;
            }

            MethodBase target = AccessTools.Method(typeof(WildPlantSpawner), "CalculatePlantsWhichCanGrowAt");
            if (target == null)
            {
                Log.Error("[RM EnvironmentalHazards] pollination-gate: WildPlantSpawner."
                    + "CalculatePlantsWhichCanGrowAt not found — rule NOT armed. The engine signature "
                    + "this patch was written against has moved.");
                return;
            }

            try
            {
                Harmony harmony = new Harmony("mandrake.rm.environmentalhazards");
                harmony.Patch(target, postfix: new HarmonyMethod(
                    typeof(RM_PollinationGatePatch), nameof(CalculatePlantsWhichCanGrowAt_Postfix)));
            }
            catch (Exception e)
            {
                Log.Error("[RM EnvironmentalHazards] pollination-gate: patch failed, rule NOT armed. " + e);
            }
        }

        // outPlants is mutated in place by the original method; Harmony hands
        // a postfix the same List<ThingDef> reference, so removing from it
        // here is visible to the caller with no return-value dance (same
        // shape as RM_LeachmossWildSpawnGatePatch).
        public static void CalculatePlantsWhichCanGrowAt_Postfix(WildPlantSpawner __instance, List<ThingDef> outPlants)
        {
            if (!RM_EnvironmentalHazardsSettings.pollinationGateEnabled)
            {
                return;
            }
            if (outPlants == null || outPlants.Count == 0 || mapRef == null)
            {
                return;
            }

            Map map;
            try
            {
                map = mapRef(__instance);
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RM EnvironmentalHazards] pollination-gate: could not read owning "
                    + "map, rule inert this call. " + e.Message, 0x504F4C31);
                return;
            }
            if (map == null)
            {
                return;
            }

            try
            {
                for (int i = outPlants.Count - 1; i >= 0; i--)
                {
                    ThingDef candidate = outPlants[i];
                    RM_PollinationGateExtension ext = candidate?.GetModExtension<RM_PollinationGateExtension>();
                    if (ext?.pollinatorRace == null)
                    {
                        continue;
                    }
                    if (map.listerThings.ThingsOfDef(ext.pollinatorRace).Count == 0)
                    {
                        outPlants.RemoveAt(i);
                    }
                }
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RM EnvironmentalHazards] pollination-gate: " + e.Message, 0x504F4C32);
            }
        }
    }
}
