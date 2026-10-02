using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.MovingDunes
{
    /// <summary>
    /// STILLSAND_GLASS_LENS_CHAIN_1 §1 — every drift is stock. Owner ruling by card
    /// 2026-09-30 (reverses this engine's old "dig vanishes"): shovelling drift through
    /// vanilla's <c>Area_SnowOrSandClear</c> / <c>WorkGiver_ClearSnowOrSand</c> drops the
    /// biome's <see cref="DuneFieldExtension.clearYield"/> in proportion to the sand depth
    /// removed, with no loss factor.
    ///
    /// The vanilla driver zeroes the cell inside a closure on its clear toil's
    /// <c>tickIntervalAction</c> (decompiled 1.6 <c>JobDriver_ClearSnowAndSand</c>), so
    /// this postfix wraps that action: read the cell's sand depth, run vanilla, read it
    /// again, and pay out the difference. Patching <c>SandGrid.SetDepth</c> instead would
    /// also catch the transport engine's own writes.
    ///
    /// Mass cap: the removed sand is simply gone from the grid, and the cap in
    /// <c>MapComponent_DuneField.RunInflux</c> is computed from <c>SandGrid.TotalDepth</c>,
    /// so shovelled sand leaves the field and influx may replace it, as designed.
    /// </summary>
    public static class Patch_ClearSand_Yield
    {
        public static void Postfix(JobDriver_ClearSnowAndSand __instance, ref IEnumerable<Toil> __result)
        {
            __result = Wrap(__instance, __result);
        }

        private static IEnumerable<Toil> Wrap(JobDriver_ClearSnowAndSand driver, IEnumerable<Toil> toils)
        {
            foreach (Toil toil in toils)
            {
                if (toil != null && toil.tickIntervalAction != null)
                {
                    Action<int> vanilla = toil.tickIntervalAction;
                    toil.tickIntervalAction = delta => TickWithYield(driver, vanilla, delta);
                }
                yield return toil;
            }
        }

        private static void TickWithYield(JobDriver_ClearSnowAndSand driver, Action<int> vanilla, int delta)
        {
            Map map = driver.pawn?.Map;
            IntVec3 cell = driver.job != null ? driver.job.targetA.Cell : IntVec3.Invalid;
            float before = (map != null && cell.IsValid && cell.InBounds(map) && map.sandGrid != null)
                ? map.sandGrid.GetDepth(cell) : 0f;

            vanilla(delta);

            if (before <= 0f || map == null || map.sandGrid == null)
            {
                return;
            }
            float removed = before - map.sandGrid.GetDepth(cell);
            if (removed <= 0f)
            {
                return;
            }
            try
            {
                Pay(map, cell, removed);
            }
            catch (Exception e)
            {
                Log.WarningOnce(MovingDunesMod.LogPrefix + "clear-sand-yield: " + e.Message, 0x5A4D0E1);
            }
        }

        /// <summary>Drops the biome's clear yield for <paramref name="removedDepth"/> of sand.
        /// Public so a debug action or a selftest can drive it without a pawn.</summary>
        public static int Pay(Map map, IntVec3 cell, float removedDepth)
        {
            if (!MovingDunesSettings.clearYieldEnabled || DuneFieldRegistry.Get(map) == null)
            {
                return 0;
            }
            DuneFieldExtension ext = map.Biome?.GetModExtension<DuneFieldExtension>();
            if (ext == null || ext.clearYield == null)
            {
                return 0;
            }
            int count = GenMath.RoundRandom(removedDepth * ext.clearYieldPerDepth
                                            * MovingDunesSettings.clearYieldMultiplier);
            if (count <= 0)
            {
                return 0;
            }
            Thing t = ThingMaker.MakeThing(ext.clearYield);
            t.stackCount = count;
            GenPlace.TryPlaceThing(t, cell, map, ThingPlaceMode.Near);
            return count;
        }
    }
}
