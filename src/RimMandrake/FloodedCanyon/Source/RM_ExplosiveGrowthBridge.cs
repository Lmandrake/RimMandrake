using System;
using System.Collections.Generic;
using HarmonyLib;
using Verse;

namespace RimMandrake.FloodedCanyon
{
    // ════════════════════════════════════════════════════════════════════
    // The flood's soak goes to mandrake.rm.explosivegrowth — by reflection, so
    // this biome mod keeps no hard dependency on it. Without that mod the
    // flood still floods, chimes and leaves soil; it simply soaks nothing.
    //
    // This REPLACES this mod's former RM_Patch_Plant_GrowthRate (a flat
    // decaying x6 GrowthRate postfix on flooded cells, whose own comment
    // called itself "NOT the full ... engine drafted for the separate,
    // larger, unbuilt EXPLOSIVE_PLANT_GROWTH_1 item"). That engine now
    // exists; running both would have multiplied flooded ground twice.
    // ════════════════════════════════════════════════════════════════════
    public static class RM_ExplosiveGrowthBridge
    {
        private static bool resolved;
        private static Func<Map, IEnumerable<IntVec3>, int, int> soakCells;

        public static bool Available
        {
            get
            {
                Resolve();
                return soakCells != null;
            }
        }

        private static void Resolve()
        {
            if (resolved) return;
            resolved = true;
            try
            {
                var m = AccessTools.Method("RimMandrake.ExplosiveGrowth.ExplosiveGrowthAPI:SoakCells");
                if (m != null)
                {
                    soakCells = (Func<Map, IEnumerable<IntVec3>, int, int>)Delegate.CreateDelegate(
                        typeof(Func<Map, IEnumerable<IntVec3>, int, int>), m);
                }
            }
            catch (Exception e)
            {
                Log.Warning("[RM FloodedCanyon] Explosive Growth API present but unbindable; the flood will soak nothing: " + e.Message);
                soakCells = null;
            }
        }

        public static int SoakCells(Map map, IEnumerable<IntVec3> cells, int ticks)
        {
            Resolve();
            if (soakCells == null) return 0;
            try
            {
                return soakCells(map, cells, ticks);
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RM FloodedCanyon] Explosive Growth soak call failed: " + e.Message, 0x7F10AD);
                return 0;
            }
        }
    }
}
