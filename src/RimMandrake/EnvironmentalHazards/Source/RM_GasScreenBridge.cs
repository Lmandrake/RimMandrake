using System;
using System.Reflection;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    /// <summary>SCREEN_STOPS_SPORES_1: asks the Scarlands aerosol screen (RM_CompAerosolScreen.IsPositionScreened) whether a cell is
    /// inside a live screen's dome. EnvironmentalHazards does not reference Scarlands, so the test is resolved by name once and
    /// held as a delegate; with Scarlands absent every cell reads unscreened. Callers gate on screenStopsSporesEnabled.</summary>
    public static class RM_GasScreenBridge
    {
        public const string ScreenTypeName = "RimMandrake.Scarlands.RM_CompAerosolScreen";
        private static Func<IntVec3, Map, bool> test;
        private static bool resolved;

        /// <summary>True once the screen test has been found (a dev/bridge read).</summary>
        public static bool Resolved { get { Resolve(); return test != null; } }

        private static void Resolve()
        {
            if (resolved) return;
            resolved = true;
            Type t = GenTypes.GetTypeInAnyAssembly(ScreenTypeName);
            MethodInfo m = t?.GetMethod("IsPositionScreened", BindingFlags.Public | BindingFlags.Static, null, new[] { typeof(IntVec3), typeof(Map) }, null);
            if (m != null) test = (Func<IntVec3, Map, bool>)Delegate.CreateDelegate(typeof(Func<IntVec3, Map, bool>), m);
        }

        public static bool IsScreened(IntVec3 cell, Map map)
        {
            Resolve();
            return test != null && map != null && test(cell, map);
        }
    }
}
