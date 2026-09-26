using System;
using HarmonyLib;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ════════════════════════════════════════════════════════════════════
    // GREENTIDE_MECHANICS_2 M2 + M10 → EXPLOSIVE_PLANT_GROWTH_1's grid.
    //
    // Both hooks were built as documented no-ops waiting on "the same
    // EXPLOSIVE_PLANT_GROWTH_1 suppression grid" (greentide_kit_spec.md M2,
    // M10). That grid now exists in mandrake.rm.explosivegrowth
    // (RM_MapComponent_ExplosiveGrowth.Suppress): encroachment pressure there
    // IS soak, so suppression refuses new soak on the cell, dries what is
    // there, makes a charging plant relax, and keeps sown rings (Churn and
    // Burst alike) off it until it decays.
    //
    // Called by REFLECTION through the engine's public API
    // (ExplosiveGrowthAPI.Suppress(Map, IntVec3, int radius, int ticks)) so
    // this shared kit takes no hard dependency on that mod: without it both
    // hooks stay armed and do nothing, exactly as before.
    // ════════════════════════════════════════════════════════════════════
    public static class RM_ExplosiveGrowthSuppressionBridge
    {
        // greentide_kit_spec.md M10: "a decay of a few days" — INVENTED 3.
        public const int GrazingSuppressionTicks = 3 * 60000;

        private static bool resolved;
        private static Action<Map, IntVec3, int, int> suppress;

        public static bool Available
        {
            get { Resolve(); return suppress != null; }
        }

        private static void Resolve()
        {
            if (resolved) return;
            resolved = true;
            try
            {
                var m = AccessTools.Method("RimMandrake.ExplosiveGrowth.ExplosiveGrowthAPI:Suppress");
                if (m != null)
                {
                    suppress = (Action<Map, IntVec3, int, int>)Delegate.CreateDelegate(
                        typeof(Action<Map, IntVec3, int, int>), m);
                }
            }
            catch (Exception e)
            {
                Log.Warning("[RM EnvironmentalHazards] Explosive Growth API present but unbindable; grazing/blower suppression is a no-op: " + e.Message);
                suppress = null;
            }
        }

        public static void Suppress(Map map, IntVec3 cell, int radius, int ticks)
        {
            Resolve();
            if (suppress == null || map == null) return;
            suppress(map, cell, radius, ticks);
        }
    }
}
