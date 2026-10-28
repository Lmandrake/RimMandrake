using System;
using System.Diagnostics;
using HarmonyLib;
using RimMandrake.Shared;
using Verse;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>HOSE_DRAW_FIX_STALLS_WHILE_WORKER_LAYS (live round 9 T2: one 2368 ms DoSingleTick while workers laid, its
    /// hose share unnamed): the slowest game tick since the last read, with what ran inside it -- garbage collections (a
    /// full Boehm collection on this heap is ~1.3 s), the hose map components' own time, whole-map world rebuilds and their
    /// time, lays started -- so a round names the spike instead of guessing. Two timestamps per tick; read and reset
    /// through jawa/static_call RimMandrake.FlowWorks.Hose.HoseTickWatch.Read("1") ("0" reads without resetting).</summary>
    [HarmonyPatch(typeof(TickManager), nameof(TickManager.DoSingleTick))]
    [PatchFeature("Flexible hoses: worst-tick watch", typeof(RM_HoseSettings), "enabled")]
    public static class HoseTickWatch
    {
        private static long t0, hose0, builds0, buildTicks0, lays0;
        private static int gc0, gcAll0;
        private static long hoseTicks;
        private static long ticks;

        // the worst tick since the last reset
        private static double worstMs, worstHoseMs, worstBuildMs;
        private static int worstTick = -1, worstGc0, worstGcAll, worstBuilds, worstLays;

        [HarmonyPrefix]
        public static void Prefix()
        {
            gc0 = GC.CollectionCount(0);
            gcAll0 = GC.CollectionCount(GC.MaxGeneration);
            hose0 = hoseTicks;
            builds0 = RM_MapComponent_Hoses.WorldBuilds;
            buildTicks0 = RM_MapComponent_Hoses.BuildWorldStopwatchTicks;
            lays0 = HoseLayQueue.AllStarted;
            t0 = Stopwatch.GetTimestamp();
        }

        [HarmonyPostfix]
        public static void Postfix()
        {
            long dt = Stopwatch.GetTimestamp() - t0;
            ticks++;
            double ms = dt * 1000.0 / Stopwatch.Frequency;
            if (ms <= worstMs) return;
            worstMs = ms;
            worstTick = Find.TickManager?.TicksGame ?? -1;
            worstGc0 = GC.CollectionCount(0) - gc0;
            worstGcAll = GC.CollectionCount(GC.MaxGeneration) - gcAll0;
            worstHoseMs = (hoseTicks - hose0) * 1000.0 / Stopwatch.Frequency;
            worstBuilds = (int)(RM_MapComponent_Hoses.WorldBuilds - builds0);
            worstBuildMs = (RM_MapComponent_Hoses.BuildWorldStopwatchTicks - buildTicks0) * 1000.0 / Stopwatch.Frequency;
            worstLays = (int)(HoseLayQueue.AllStarted - lays0);
        }

        /// <summary>The hose map component's MapComponentTick time, Stopwatch ticks (its own Harmony pair below).</summary>
        [HarmonyPatch(typeof(RM_MapComponent_Hoses), nameof(RM_MapComponent_Hoses.MapComponentTick))]
        [PatchFeature("Flexible hoses: worst-tick watch", typeof(RM_HoseSettings), "enabled")]
        public static class HoseShare
        {
            private static long s0;
            [HarmonyPrefix] public static void Prefix() => s0 = Stopwatch.GetTimestamp();
            [HarmonyPostfix] public static void Postfix() => hoseTicks += Stopwatch.GetTimestamp() - s0;
        }

        /// <summary>Static-call hook: the worst tick since the last reset as JSON; "1" also resets it.</summary>
        public static string Read(string reset)
        {
            string j = "{\"ticks\":" + ticks + ",\"worstMs\":" + worstMs.ToString("0.0") + ",\"tick\":" + worstTick
                + ",\"gc0\":" + worstGc0 + ",\"gcFull\":" + worstGcAll + ",\"hoseMs\":" + worstHoseMs.ToString("0.0")
                + ",\"worldBuilds\":" + worstBuilds + ",\"buildWorldMs\":" + worstBuildMs.ToString("0.0")
                + ",\"laysStarted\":" + worstLays + "}";
            if (reset == "1") { ticks = 0; worstMs = 0; worstTick = -1; worstGc0 = worstGcAll = worstBuilds = worstLays = 0; worstHoseMs = worstBuildMs = 0; }
            return j;
        }
    }
}
