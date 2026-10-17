using System;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace RimMandrake.Shared
{
    // ════════════════════════════════════════════════════════════════════
    // FlowWorks' SPRINKLED cells, read reflection-soft (SPRINKLER_HEADS_BUILD_PUMP_REQUIRED, design sprinklers_design_2026-10-16
    // §4), the twin of FlowWorksIrrigationRead: FlowWorks is never a dependency. The seam is two static methods on
    // RimMandrake.FlowWorks.Sprinklers.RM_MapComponent_Sprinklers:
    //   bool WetAt(Map, IntVec3, out string liquidKey)   the cell is sprinkled now; liquidKey = the FluidDef defName that wets it
    //   bool Spend(Map, IntVec3)                         EC3: a fruiting crop used the water; dry until the next paid pulse
    // With FlowWorks absent (or an older one without sprinklers) Available is false and every read is silent.
    // ════════════════════════════════════════════════════════════════════
    public static class FlowWorksSprinklerRead
    {
        private static bool resolved;
        private delegate bool WetAtFn(Map map, IntVec3 c, out string liquidKey);
        private static WetAtFn wetAt;
        private static Func<Map, IntVec3, bool> spend;

        public static bool Available
        {
            get { Resolve(); return wetAt != null; }
        }

        private static void Resolve()
        {
            if (resolved) return;
            resolved = true;
            try
            {
                Type t = AccessTools.TypeByName("RimMandrake.FlowWorks.Sprinklers.RM_MapComponent_Sprinklers");
                if (t == null) return;
                MethodInfo w = AccessTools.Method(t, "WetAt", new[] { typeof(Map), typeof(IntVec3), typeof(string).MakeByRefType() });
                MethodInfo s = AccessTools.Method(t, "Spend", new[] { typeof(Map), typeof(IntVec3) });
                if (w == null || !w.IsStatic || w.ReturnType != typeof(bool))
                {
                    Log.Warning("[RimMandrake] FlowWorks sprinkler read: WetAt(Map, IntVec3, out string) not found; sprinkled cells read dry.");
                    return;
                }
                wetAt = (WetAtFn)Delegate.CreateDelegate(typeof(WetAtFn), w);   // no per-read allocation (IRM_WetSource.WetFor)
                if (s != null && s.IsStatic && s.ReturnType == typeof(bool))
                {
                    spend = (Func<Map, IntVec3, bool>)Delegate.CreateDelegate(typeof(Func<Map, IntVec3, bool>), s);
                }
            }
            catch (Exception e)
            {
                Log.Warning("[RimMandrake] FlowWorks sprinkler reflection failed; sprinkled cells read dry: " + e.Message);
                wetAt = null;
                spend = null;
            }
        }

        /// <summary>The liquid key sprinkled on <paramref name="c"/> now, or null.</summary>
        public static string WetKey(Map map, IntVec3 c)
        {
            Resolve();
            return wetAt == null || map == null || !wetAt(map, c, out string key) ? null : key;
        }

        public static bool Spend(Map map, IntVec3 c)
        {
            Resolve();
            return spend != null && map != null && spend(map, c);
        }
    }
}
