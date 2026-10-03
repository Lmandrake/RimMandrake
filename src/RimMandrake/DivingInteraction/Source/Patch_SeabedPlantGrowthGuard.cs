using System;
using HarmonyLib;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // SEABED_PER_SEA_FLOORS_1 (Phase 3 guard). MapPlantGrowthRateCalculator.BuildFor(Map) runs in
    // Map.FinalizeInit and samples OutdoorTemperatureAt(map.Tile) for every wild grazing plant.
    // A throw there leaves a map that is already in Find.Maps unfinished (MapDrawer NREs every
    // frame). Vanilla is safe off-surface only because those biomes have no wild plants.
    //
    // This finalizer swallows the exception for maps on the seabed layer ONLY and logs once.
    // ComputeIfDirty clears its dirty flag before any sampling, so later accessors do not
    // re-throw; the pasture-nutrition numbers for a floor map may be partial, which nothing on
    // the floor reads. Surface maps keep vanilla behaviour untouched.
    // UNPROVEN LIVE: the decompiled TileTemperaturesComp keys its cache per layer, so the crash
    // may not reproduce in 1.6; the guard is cheap insurance until a floor map with plants loads.
    [HarmonyPatch(typeof(MapPlantGrowthRateCalculator), nameof(MapPlantGrowthRateCalculator.BuildFor), new[] { typeof(Map) })]
    public static class Patch_SeabedPlantGrowthGuard
    {
        private static bool logged;

        public static Exception Finalizer(Exception __exception, Map map)
        {
            if (__exception == null || map == null || !RM_SeabedLayerUtility.IsSeabedTile(map.Tile))
            {
                return __exception;
            }

            if (!logged)
            {
                logged = true;
                Log.Warning("[RimMandrake.DivingInteraction] Plant growth-rate calculator threw on a sea-floor map and was guarded: " + __exception.GetType().Name + ": " + __exception.Message);
            }

            return null;
        }
    }
}
