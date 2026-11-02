using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // SEABED_DESCENT_ASCENT_1: fuel cost per depth, both ways.
    //
    // Every gravship fuel price in the game goes through GravshipUtility.TryGetPathFuelCost: the pilot console's
    // tile-picker validator and its mouse-over "Cost:" text, and Building_GravEngine.ConsumeFuel at launch (read in
    // the 1.6 decompile, 2026-11-02). A postfix there therefore prices the dialog, refuses a short tank and burns
    // the same number, with no second copy of the rule. The vanilla body caches its last answer and returns the
    // cached cost early; the postfix runs after both paths and adds to the out value only, never the cache, so a
    // repeated query is priced the same every time.
    //
    // The ring the console draws (GravshipUtility.MaxDistForFuel) is per LAYER with no tile, so it cannot show a
    // depth; it is left vanilla and may overstate reach on the floor layer. The validator above is the authority.
    [HarmonyPatch(typeof(GravshipUtility), nameof(GravshipUtility.TryGetPathFuelCost))]
    public static class Patch_SeabedDescentFuel
    {
        public static void Postfix(PlanetTile from, PlanetTile to, ref float cost, bool __result)
        {
            if (!__result || !RM_DivingSettings.seabedDescentDepthFuelEnabled) return;
            cost += ExtraFor(from, to);
        }

        public static float ExtraFor(PlanetTile from, PlanetTile to)
        {
            if (!from.Valid || !to.Valid || Find.WorldGrid == null) return 0f;
            bool fromFloor = RM_SeabedLayerUtility.IsSeabedTile(from);
            bool toFloor = RM_SeabedLayerUtility.IsSeabedTile(to);
            SurfaceLayer surface = Find.WorldGrid.Surface;
            bool fromSurface = from.Layer == surface;
            bool toSurface = to.Layer == surface;
            PlanetTile floorEnd = fromFloor ? from : to;
            float elevation = (fromFloor || toFloor) && floorEnd.Tile != null ? floorEnd.Tile.elevation : 0f;
            return RM_SeabedDescentKernel.ExtraFuel(fromFloor, fromSurface, toFloor, toSurface, elevation,
                RM_DivingSettings.seabedDescentFuelPerMeter);
        }
    }
}
