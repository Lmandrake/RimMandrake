// JawaBenchTpsProfiler.cs - continuous COARSE attribution of tick cost (BRIDGE_TPS_CAPTURE_FIXES_1, item 5).
//
// Prefix/postfix timers (Stopwatch ticks, no allocation) on the ten coarse stages of
// Verse.TickManager.DoSingleTick (decompiled 1.6): the whole tick, the three TickList categories
// (Normal/Rare/Long, by the list's own tickType), World.WorldTick, World.WorldPostTick, Map.MapPreTick,
// Map.MapPostTick, MapComponentUtility.MapComponentTick (NESTED inside MapPostTick) and
// GameComponentUtility.GameComponentTick. Per window: count, total ms, max ms of each (INCLUSIVE),
// the largest EXCLUSIVE stage as `top`, and up to WorstTicks worst single ticks with their breakdown.
// Everything else DoSingleTick does (storyteller, quests, letters, history, autosaver tick, ...) is
// `tickOther` = tick minus its timed children.
//
// ⚖️ MEASURED-OVERHEAD DISCIPLINE: at install the cost of one timer pair is calibrated on this machine
// and every window reports profHooks (timer pairs fired) and profEstMs (hooks x calibrated cost). That is
// a LOWER bound - Harmony's trampoline cost is not in the calibration - so the real figure is owed
// from a live A/B on the full mod list (criterion C3) and the doc says so. The profiler can be switched
// off in tps_settings.json ("attribution": false) without touching the TPS windows.
// ⛔ SKIP by ruling: per-method / per-pawn / per-mod instrumentation stays out of the always-on path.

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.Reflection;
using System.Text;
using HarmonyLib;
using RimWorld.Planet;
using Verse;
using M = JawaBench.BridgeTools.JawaBenchTpsMath;
using WD = JawaBench.BridgeTools.JawaBenchTpsWatchdog;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchTpsProfiler
    {
        internal const int CTick = 0, CNormal = 1, CRare = 2, CLong = 3, CWorld = 4, CWorldPost = 5, CMapPre = 6,
            CMapPost = 7, CMapComp = 8, CGameComp = 9, N = 10;
        internal static readonly string[] Names =
            { "tick", "tl:Normal", "tl:Rare", "tl:Long", "world", "worldPost", "mapPre", "mapPost", "mapComp", "gameComp" };
        private const int WorstTicks = 3;
        private const double WorstTickSeconds = 0.030;

        private static readonly long[] Count = new long[N];
        private static readonly long[] Total = new long[N];
        private static readonly long[] Max = new long[N];
        private static readonly long[] TickBase = new long[N];
        private static readonly List<string> Worst = new List<string>();
        private static readonly List<long> WorstTicksMs = new List<long>();
        private static long _hooks;

        internal static bool Installed;
        internal static string InstallError;
        internal static double CostPerPairSeconds;
        internal static int PatchedStages;

        private static AccessTools.FieldRef<TickList, TickerType> _tickType;

        internal static void Install(Harmony h)
        {
            try
            {
                _tickType = AccessTools.FieldRefAccess<TickList, TickerType>("tickType");
                var self = typeof(JawaBenchTpsProfiler);
                Patch(h, AccessTools.Method(typeof(TickManager), nameof(TickManager.DoSingleTick)), "TickPre", "TickPost");
                Patch(h, AccessTools.Method(typeof(TickList), nameof(TickList.Tick)), "TlPre", "TlPost");
                Patch(h, AccessTools.Method(typeof(World), nameof(World.WorldTick)), "WorldPre", "WorldPost");
                Patch(h, AccessTools.Method(typeof(World), nameof(World.WorldPostTick)), "WorldPostPre", "WorldPostPost");
                Patch(h, AccessTools.Method(typeof(Map), nameof(Map.MapPreTick)), "MapPrePre", "MapPrePost");
                Patch(h, AccessTools.Method(typeof(Map), nameof(Map.MapPostTick)), "MapPostPre", "MapPostPost");
                Patch(h, AccessTools.Method(typeof(MapComponentUtility), nameof(MapComponentUtility.MapComponentTick)), "MapCompPre", "MapCompPost");
                Patch(h, AccessTools.Method(typeof(GameComponentUtility), nameof(GameComponentUtility.GameComponentTick)), "GameCompPre", "GameCompPost");
                Calibrate();
                Installed = true;
            }
            catch (Exception e)
            {
                InstallError = e.GetType().Name + ": " + e.Message;
            }
        }

        private static void Patch(Harmony h, MethodInfo m, string pre, string post)
        {
            if (m == null) { InstallError = (InstallError ?? "") + pre + ": target missing; "; return; }
            var t = typeof(JawaBenchTpsProfiler);
            h.Patch(m, prefix: new HarmonyMethod(t.GetMethod(pre, BindingFlags.Static | BindingFlags.NonPublic)),
                    postfix: new HarmonyMethod(t.GetMethod(post, BindingFlags.Static | BindingFlags.NonPublic)));
            PatchedStages++;
        }

        private static void Calibrate()
        {
            const int n = 20000;
            var sw = Stopwatch.StartNew();
            long sink = 0;
            for (int i = 0; i < n; i++)
            {
                long s = Stopwatch.GetTimestamp();
                long d = Stopwatch.GetTimestamp() - s;
                sink += d;
            }
            sw.Stop();
            CostPerPairSeconds = sw.Elapsed.TotalSeconds / n;
            GC.KeepAlive(sink);
        }

        // ---- stage timers (main thread) ---------------------------------------------------------
        private static long Begin(int phase)
        {
            WD.Enter(phase);
            return Stopwatch.GetTimestamp();
        }

        private static void End(int c, long start)
        {
            long d = Stopwatch.GetTimestamp() - start;
            Count[c]++;
            Total[c] += d;
            if (d > Max[c]) Max[c] = d;
            _hooks++;
            WD.Exit();
        }

        private static void TickPre(out long __state)
        {
            Array.Copy(Total, TickBase, N);
            __state = Begin(WD.PTick);
        }

        private static void TickPost(long __state)
        {
            End(CTick, __state);
            long d = Stopwatch.GetTimestamp() - __state;
            if ((double)d / Stopwatch.Frequency >= WorstTickSeconds) NoteWorst(d);
        }

        private static int TlCat(TickList l)
        {
            switch (_tickType(l)) { case TickerType.Rare: return CRare; case TickerType.Long: return CLong; default: return CNormal; }
        }

        private static void TlPre(TickList __instance, out long __state) { __state = Begin(WD.PTlNormal + TlCat(__instance) - CNormal); }
        private static void TlPost(TickList __instance, long __state) { End(TlCat(__instance), __state); }
        private static void WorldPre(out long __state) { __state = Begin(WD.PWorld); }
        private static void WorldPost(long __state) { End(CWorld, __state); }
        private static void WorldPostPre(out long __state) { __state = Begin(WD.PWorldPost); }
        private static void WorldPostPost(long __state) { End(CWorldPost, __state); }
        private static void MapPrePre(out long __state) { __state = Begin(WD.PMapPre); }
        private static void MapPrePost(long __state) { End(CMapPre, __state); }
        private static void MapPostPre(out long __state) { __state = Begin(WD.PMapPost); }
        private static void MapPostPost(long __state) { End(CMapPost, __state); }
        private static void MapCompPre(out long __state) { __state = Begin(WD.PMapComp); }
        private static void MapCompPost(long __state) { End(CMapComp, __state); }
        private static void GameCompPre(out long __state) { __state = Begin(WD.PGameComp); }
        private static void GameCompPost(long __state) { End(CGameComp, __state); }

        private static double Ms(long ticks) => ticks * 1000.0 / Stopwatch.Frequency;

        private static void NoteWorst(long d)
        {
            long ms = (long)Ms(d);
            if (Worst.Count >= WorstTicks)
            {
                int min = 0;
                for (int i = 1; i < WorstTicksMs.Count; i++) if (WorstTicksMs[i] < WorstTicksMs[min]) min = i;
                if (WorstTicksMs[min] >= ms) return;
                Worst.RemoveAt(min);
                WorstTicksMs.RemoveAt(min);
            }
            var delta = new long[N];
            for (int i = 0; i < N; i++) delta[i] = Total[i] - TickBase[i];
            delta[CTick] = d;
            Worst.Add("{\"tg\":" + WD.LastTicksGame + ",\"ms\":" + M.F(Ms(d), 1) + ",\"top\":\"" + Top(delta) + "\"}");
            WorstTicksMs.Add(ms);
        }

        /// <summary>Exclusive stage times from inclusive totals: tick minus children, mapPost minus mapComp.</summary>
        private static long[] Exclusive(long[] t)
        {
            var x = (long[])t.Clone();
            x[CTick] = t[CTick] - t[CNormal] - t[CRare] - t[CLong] - t[CWorld] - t[CWorldPost] - t[CMapPre] - t[CMapPost] - t[CGameComp];
            x[CMapPost] = t[CMapPost] - t[CMapComp];
            if (x[CTick] < 0) x[CTick] = 0;
            if (x[CMapPost] < 0) x[CMapPost] = 0;
            return x;
        }

        private static string Top(long[] totals)
        {
            var x = Exclusive(totals);
            if (totals[CTick] <= 0) return "";
            int best = -1;
            for (int i = 0; i < N; i++) if (best < 0 || x[i] > x[best]) best = i;
            string name = best == CTick ? "tickOther" : Names[best];
            return name + " " + ((int)Math.Round(100.0 * x[best] / totals[CTick])).ToString(CultureInfo.InvariantCulture) + "%";
        }

        /// <summary>This window's attribution as JSON fields (no braces), then reset. Main thread.</summary>
        internal static string TakeWindowFields()
        {
            if (!Installed) return "\"attr\":null";
            var sb = new StringBuilder(600);
            sb.Append("\"attr\":{");
            for (int i = 0; i < N; i++)
            {
                if (i > 0) sb.Append(',');
                sb.Append('"').Append(Names[i]).Append("\":[").Append(Count[i]).Append(',')
                  .Append(M.F(Ms(Total[i]), 1)).Append(',').Append(M.F(Ms(Max[i]), 1)).Append(']');
            }
            sb.Append('}');
            sb.Append(",\"top\":\"").Append(Top(Total)).Append('"');
            sb.Append(",\"worst\":[").Append(string.Join(",", Worst.ToArray())).Append(']');
            sb.Append(",\"profHooks\":").Append(_hooks);
            sb.Append(",\"profEstMs\":").Append(M.F(_hooks * CostPerPairSeconds * 1000.0, 2));
            Array.Clear(Count, 0, N);
            Array.Clear(Total, 0, N);
            Array.Clear(Max, 0, N);
            Worst.Clear();
            WorstTicksMs.Clear();
            _hooks = 0;
            return sb.ToString();
        }
    }
}
