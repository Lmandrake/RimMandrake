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
    // NOT calling into a real grid this pass: confirmed by grep before
    // writing this file (grep -rn "ExplosivePlantGrowth\|SuppressionGrid"
    // src/, zero hits outside this file's own TODO marker below) that
    // EXPLOSIVE_PLANT_GROWTH_1 — a separate, larger, BENCH-owned item — has
    // not shipped its suppression-grid engine yet (still design-only per
    // infrastructure/state/items/EXPLOSIVE_PLANT_GROWTH_1.md, re-checked
    // 2026-09-26: still "doing", only the design doc exists). Building that
    // grid here would be doing a different item's whole job inside this
    // hook — exactly the trap RM_CompDryFieldEmitter.SuppressPlantGrowth()
    // (M2, same kit) already declined for the identical reason. This hook
    // follows that same precedent: the seam is proven and armed, the actual
    // grid write is a documented no-op with a TODO naming the item that
    // owns it, so the day that grid ships, only WriteSuppression's body
    // needs filling in — no new patch, no new choke-point hunt.
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

        // TODO(EXPLOSIVE_PLANT_GROWTH_1): once that engine's suppression
        // grid exists, call its write here for `cell` at `SuppressionRadius`
        // on `map` — do not build a new grid in this method when that day
        // comes, call into the real one. `ingester` is threaded through
        // already (unused today) since the real engine may want to
        // distinguish a wild grazer from a player-owned animal or a
        // colonist eating raw.
        private static void WriteSuppression(IntVec3 cell, Map map, Pawn ingester)
        {
        }
    }
}
