using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M10 (greentide_kit_spec.md "M10. Grazing
    // suppresses encroachment", §4): "grazing events write suppression into
    // the same EXPLOSIVE_PLANT_GROWTH_1 suppression grid the blower (M2)
    // writes." Choke-point CONFIRMED by this item's own 2026-09-13 spike
    // pass against the real 1.6/Odyssey decompile, re-cited not
    // re-verified: RimWorld/Plant.cs:603
    // Plant.IngestedCalculateAmounts(Pawn ingester, float nutritionWanted,
    // out int numTaken, out float nutritionIngested) is the single seam
    // every plant-eating pawn passes through via the base Thing.Ingested —
    // grazing animal or player alike, no separate route. A postfix here is
    // the whole mechanism per the spec's own text ("zero new defs — any
    // plant-eater suppresses, which is exactly the sheet's ecology").
    //
    // WIRED 2026-09-26: the grid this hook was built to write into now
    // exists (mandrake.rm.explosivegrowth, EXPLOSIVE_PLANT_GROWTH_1). The
    // write goes through RM_ExplosiveGrowthSuppressionBridge by reflection,
    // so this kit still takes no hard dependency on that mod — without it
    // the hook stays armed and writes nothing.
    [StaticConstructorOnStartup]
    public static class RM_GrazingSuppressionHookPatch
    {
        static RM_GrazingSuppressionHookPatch()
        {
            var target = AccessTools.Method(typeof(Plant), "IngestedCalculateAmounts");
            if (target == null)
            {
                Log.Error("[RM EnvironmentalHazards] grazing-suppression-hook: Plant."
                    + "IngestedCalculateAmounts not found — hook NOT armed. The engine "
                    + "signature this patch was written against has moved.");
                return;
            }

            try
            {
                Harmony harmony = new Harmony("mandrake.rm.environmentalhazards");
                harmony.Patch(target, postfix: new HarmonyMethod(
                    typeof(RM_GrazingSuppressionHookPatch), nameof(IngestedCalculateAmounts_Postfix)));
            }
            catch (Exception e)
            {
                Log.Error("[RM EnvironmentalHazards] grazing-suppression-hook: patch failed, "
                    + "hook NOT armed. " + e);
            }
        }

        // INVENTED (kit spec M10's own text): "recording cell + radius 1
        // suppression with a decay of a few days" — the radius constant
        // lives here so the future grid write and this hook agree on it
        // without a second invented number appearing when that day comes.
        public const int SuppressionRadius = 1;

        public static void IngestedCalculateAmounts_Postfix(Plant __instance, Pawn ingester)
        {
            if (!RM_EnvironmentalHazardsSettings.grazingSuppressionHookEnabled)
            {
                return;
            }

            if (__instance == null || !__instance.Spawned || __instance.Map == null)
            {
                return;
            }

            try
            {
                WriteSuppression(__instance.Position, __instance.Map, ingester);
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RM EnvironmentalHazards] grazing-suppression-hook: " + e.Message, 0x475348);
            }
        }

        // `ingester` is unused: the spec's ecology is "any plant-eater
        // suppresses" — a wild grazer, a penned herd and a colonist eating
        // raw all hold the green back the same way.
        private static void WriteSuppression(IntVec3 cell, Map map, Pawn ingester)
        {
            RM_ExplosiveGrowthSuppressionBridge.Suppress(map, cell, SuppressionRadius,
                RM_ExplosiveGrowthSuppressionBridge.GrazingSuppressionTicks);
        }
    }
}
