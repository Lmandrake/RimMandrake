using System.Runtime.CompilerServices;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.SolarMirrors
{
    /// <summary>
    /// VEE_SOLAR_REWIRE_GEOMETRY_PAINTS_IT (design/RimMandrake/vee_port_plan_2026-10-22.md §4): the VEE solar mutators'
    /// effect moved out of the tile and into geometry. A solar panel's output (vanilla: sky glow x unroofed fraction, and
    /// RM_TidalSunGlowPatch already makes the glow a function of sun elevation) is multiplied by
    /// RM_InsolationKernel.InsolationFactor(e): up to +25% (the "high-sun bonus" setting) under a high sun.
    ///
    /// e comes from the map tile's arc to the substellar point (0,0) and nothing else: no mutator, no biome, no per-biome
    /// clamp (One Direct Sun). It acts only while the planet is tidally locked (RM_TidalSunGlowPatch.TidalLockActive):
    /// on a turning world the fixed substellar point means nothing and panels keep vanilla output. Pocket maps (no
    /// planet tile) are untouched. Setting off = vanilla glow-only output.
    /// </summary>
    [HarmonyPatch(typeof(CompPowerPlantSolar), "DesiredPowerOutput", MethodType.Getter)]
    [RimMandrake.Shared.PatchFeature("Solar output follows sun height", typeof(RM_SolarMirrorsSettings), "insolationByGeometry")]
    public static class RM_Patch_CompPowerPlantSolar_Insolation
    {
        private class Box { public float elevation; }

        // Per map: the elevation is constant for a map's life (the tile never moves), so it is resolved once.
        private static readonly ConditionalWeakTable<Map, Box> elevations = new ConditionalWeakTable<Map, Box>();

        public static void Postfix(CompPowerPlantSolar __instance, ref float __result)
        {
            if (!RM_SolarMirrorsSettings.insolationByGeometry || __result <= 0f)
            {
                return;
            }
            Map map = __instance?.parent?.Map;
            if (map == null)
            {
                return;
            }
            float? e = ElevationFor(map);
            if (e.HasValue)
            {
                __result *= RM_InsolationKernel.InsolationFactor(e.Value, RM_SolarMirrorsSettings.highSunBonus);
            }
        }

        /// <summary>Sun elevation (degrees) for the map, or null where the geometric sun does not apply.</summary>
        public static float? ElevationFor(Map map)
        {
            if (map == null || !map.Tile.Valid || Find.WorldGrid == null
                || !RimMandrake.CreatureBehaviors.RM_TidalSunGlowPatch.TidalLockActive())
            {
                return null;
            }
            return elevations.GetValue(map, m =>
            {
                Vector2 longLat = Find.WorldGrid.LongLatOf(m.Tile);
                return new Box { elevation = (float)RM_InsolationKernel.ElevationDegrees(longLat.y, longLat.x) };
            }).elevation;
        }
    }
}
