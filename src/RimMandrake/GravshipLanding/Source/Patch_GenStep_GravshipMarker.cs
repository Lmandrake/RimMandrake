using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.GravshipLanding
{
    // Gen-step order on a gravship-arrival map: ReserveGravshipArea (600) sets
    // PlayerStartSpot, Fog (1500) unfogs only the flood from that spot,
    // GravshipMarker (1700) spawns the landing picker. Running after the marker
    // means the fog grid is final and parms.gravship tells us this map is an
    // arrival map -- no other map type reaches this gen step with a gravship.
    [HarmonyPatch(typeof(GenStep_GravshipMarker), nameof(GenStep_GravshipMarker.Generate))]
    public static class Patch_GenStep_GravshipMarker_Generate
    {
        [HarmonyPostfix]
        public static void Postfix(Map map, GenStepParams parms)
        {
            if (!ModsConfig.OdysseyActive || parms.gravship == null) return;
            if (!GravshipLandingSettings.revealOutdoorsBeforeLanding) return;
            int before = CountFogged(map);
            int roots = 0;
            foreach (IntVec3 c in map.AllCells)
            {
                if (!map.fogGrid.IsFogged(c) || c.Roofed(map)) continue;
                Building edifice = c.GetEdifice(map);
                if (edifice != null && edifice.def.MakeFog) continue;
                FloodFillerFog.FloodUnfog(c, map);
                roots++;
            }
            int after = CountFogged(map);
            Log.Message("[RimMandrake.GravshipLanding] arrival map " + map.Tile + ": revealed the outdoors from "
                + roots + " roots, fogged cells " + before + " -> " + after + ".");
        }

        private static int CountFogged(Map map)
        {
            int n = 0;
            foreach (IntVec3 c in map.AllCells) if (map.fogGrid.IsFogged(c)) n++;
            return n;
        }
    }
}
