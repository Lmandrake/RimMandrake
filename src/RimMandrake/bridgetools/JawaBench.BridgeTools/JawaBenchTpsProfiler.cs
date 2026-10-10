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
using S = JawaBench.BridgeTools.JawaBenchTpsStages;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchTpsProfiler
    {
        internal const int CTick = S.CTick, CNormal = S.CNormal, CRare = S.CRare, CLong = S.CLong, CWorld = S.CWorld,
            CWorldPost = S.CWorldPost, CMapPre = S.CMapPre, CMapPost = S.CMapPost, CMapComp = S.CMapComp,
            CGameComp = S.CGameComp, N = S.N;
        internal static readonly S Stages = new S(Stopwatch.Frequency);

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
                Patch(h, AccessTools.Method(typeof(TickManager), nameof(TickManager.DoSingleTick)), "TickPre", "TickFin");
                Patch(h, AccessTools.Method(typeof(TickList), nameof(TickList.Tick)), "TlPre", "TlFin");
                Patch(h, AccessTools.Method(typeof(World), nameof(World.WorldTick)), "WorldPre", "WorldFin");
                Patch(h, AccessTools.Method(typeof(World), nameof(World.WorldPostTick)), "WorldPostPre", "WorldPostFin");
                Patch(h, AccessTools.Method(typeof(Map), nameof(Map.MapPreTick)), "MapPrePre", "MapPreFin");
                Patch(h, AccessTools.Method(typeof(Map), nameof(Map.MapPostTick)), "MapPostPre", "MapPostFin");
                Patch(h, AccessTools.Method(typeof(MapComponentUtility), nameof(MapComponentUtility.MapComponentTick)), "MapCompPre", "MapCompFin");
                Patch(h, AccessTools.Method(typeof(GameComponentUtility), nameof(GameComponentUtility.GameComponentTick)), "GameCompPre", "GameCompFin");
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
                    finalizer: new HarmonyMethod(t.GetMethod(post, BindingFlags.Static | BindingFlags.NonPublic)));
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
        // MUST 2: every hook is a PREFIX (start) + a void FINALIZER (stop). A void finalizer runs whether the
        // original returned or threw and, on the installed Harmony 2.4.2, leaves the original exception to be
        // rethrown unchanged (decompiled MethodCreator.AddFinalizers) - so a throwing tick no longer leaves a
        // timer open, and we never swallow the game's exception. A finalizer whose prefix did not run sees
        // __state = 0 and records nothing (JawaBenchTpsStages.End). Our own failures are CONTAINED: any
        // exception in a hook disables attribution and is reported; none escapes into the tick.
        internal static volatile bool Disabled;
        internal static string RuntimeError;
        internal static int MainThreadId = -1;
        private static int _tickId;

        private static void Fail(Exception e)
        {
            if (Disabled) return;
            Disabled = true;
            RuntimeError = e.GetType().Name + ": " + e.Message;
        }

        private static long Begin(int phase)
        {
            if (Disabled) return 0;
            try
            {
                if (MainThreadId >= 0 && System.Threading.Thread.CurrentThread.ManagedThreadId != MainThreadId) { Stages.CountSkip(); return 0; }
                WD.Enter(phase);
                return Stopwatch.GetTimestamp();
            }
            catch (Exception e) { Fail(e); return 0; }
        }

        private static void End(int c, long start)
        {
            if (start == 0) { if (!Disabled) Stages.CountSkip(); return; }
            try
            {
                Stages.End(c, start, Stopwatch.GetTimestamp());
                WD.Exit();
            }
            catch (Exception e) { Fail(e); }
        }

        private static void TickPre(TickManager __instance, out long __state)
        {
            __state = 0;
            if (Disabled) return;
            try
            {
                Stages.TickBegin();
                _tickId = __instance != null ? __instance.TicksGame + 1 : -1;   // DoSingleTick increments first
                __state = Begin(WD.PTick);
            }
            catch (Exception e) { Fail(e); }
        }

        private static void TickFin(long __state)
        {
            if (__state == 0) { if (!Disabled) Stages.CountSkip(); return; }
            try
            {
                Stages.TickEnd(__state, Stopwatch.GetTimestamp(), _tickId);
                WD.Exit();
            }
            catch (Exception e) { Fail(e); }
        }

        private static int TlCat(TickList l)
        {
            switch (_tickType(l)) { case TickerType.Rare: return CRare; case TickerType.Long: return CLong; default: return CNormal; }
        }

        private static void TlPre(TickList __instance, out long __state)
        {
            __state = 0;
            if (Disabled) return;
            try { __state = Begin(WD.PTlNormal + TlCat(__instance) - CNormal); }
            catch (Exception e) { Fail(e); }
        }

        private static void TlFin(TickList __instance, long __state)
        {
            if (__state == 0) { if (!Disabled) Stages.CountSkip(); return; }
            int c;
            try { c = TlCat(__instance); }
            catch (Exception e) { Fail(e); return; }
            End(c, __state);
        }

        private static void WorldPre(out long __state) { __state = Begin(WD.PWorld); }
        private static void WorldFin(long __state) { End(CWorld, __state); }
        private static void WorldPostPre(out long __state) { __state = Begin(WD.PWorldPost); }
        private static void WorldPostFin(long __state) { End(CWorldPost, __state); }
        private static void MapPrePre(out long __state) { __state = Begin(WD.PMapPre); }
        private static void MapPreFin(long __state) { End(CMapPre, __state); }
        private static void MapPostPre(out long __state) { __state = Begin(WD.PMapPost); }
        private static void MapPostFin(long __state) { End(CMapPost, __state); }
        private static void MapCompPre(out long __state) { __state = Begin(WD.PMapComp); }
        private static void MapCompFin(long __state) { End(CMapComp, __state); }
        private static void GameCompPre(out long __state) { __state = Begin(WD.PGameComp); }
        private static void GameCompFin(long __state) { End(CGameComp, __state); }

        /// <summary>This window's attribution as JSON fields (no braces), then reset. Main thread.</summary>
        internal static string TakeWindowFields()
        {
            if (!Installed) return "\"attr\":null";
            if (Disabled) return "\"attr\":null,\"attrError\":" + JawaBenchTpsMath.Json(RuntimeError);
            return Stages.TakeWindowFields(CostPerPairSeconds);
        }
    }
}
