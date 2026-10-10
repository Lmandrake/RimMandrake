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
// and every window reports profHooks (timer pairs fired) and profEstMs (hooks x calibrated cost). profEstMs is
// an ESTIMATE, not a bound in either direction: Harmony's trampoline cost is not in the calibration, and
// calibration noise or JIT/cache effects can inflate it (tps_record.md). The real figure is owed from a live
// A/B on the full mod list (criterion C3). The profiler can be switched off in tps_settings.json
// ("attribution": false) without touching the TPS windows.
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

        internal const string HarmonyId = "mandrake.jawabench.tps.attr";
        internal static string InstallStatus = "not-attempted", InstallDetail;

        /// <summary>MUST 16: all eight stage targets resolved first; any patch failure rolls back every stage timer
        /// (own Harmony id), so attribution is complete, partial (a target missing - named), or failed - never a
        /// silent mixture whose totals are drained by nobody.</summary>
        internal static void Install()
        {
            try
            {
                _tickType = AccessTools.FieldRefAccess<TickList, TickerType>("tickType");
                var h = new Harmony(HarmonyId);
                var t = typeof(JawaBenchTpsProfiler);
                var map = new Dictionary<string, string[]>
                {
                    { "DoSingleTick", new[] { "TickPre", "TickFin" } }, { "TickList.Tick", new[] { "TlPre", "TlFin" } },
                    { "WorldTick", new[] { "WorldPre", "WorldFin" } }, { "WorldPostTick", new[] { "WorldPostPre", "WorldPostFin" } },
                    { "MapPreTick", new[] { "MapPrePre", "MapPreFin" } }, { "MapPostTick", new[] { "MapPostPre", "MapPostFin" } },
                    { "MapComponentTick", new[] { "MapCompPre", "MapCompFin" } }, { "GameComponentTick", new[] { "GameCompPre", "GameCompFin" } },
                };
                var targets = new List<JawaBenchTpsInstall.Target>
                {
                    new JawaBenchTpsInstall.Target("DoSingleTick", true, () => AccessTools.Method(typeof(TickManager), nameof(TickManager.DoSingleTick))),
                    new JawaBenchTpsInstall.Target("TickList.Tick", false, () => AccessTools.Method(typeof(TickList), nameof(TickList.Tick))),
                    new JawaBenchTpsInstall.Target("WorldTick", false, () => AccessTools.Method(typeof(World), nameof(World.WorldTick))),
                    new JawaBenchTpsInstall.Target("WorldPostTick", false, () => AccessTools.Method(typeof(World), nameof(World.WorldPostTick))),
                    new JawaBenchTpsInstall.Target("MapPreTick", false, () => AccessTools.Method(typeof(Map), nameof(Map.MapPreTick))),
                    new JawaBenchTpsInstall.Target("MapPostTick", false, () => AccessTools.Method(typeof(Map), nameof(Map.MapPostTick))),
                    new JawaBenchTpsInstall.Target("MapComponentTick", false, () => AccessTools.Method(typeof(MapComponentUtility), nameof(MapComponentUtility.MapComponentTick))),
                    new JawaBenchTpsInstall.Target("GameComponentTick", false, () => AccessTools.Method(typeof(GameComponentUtility), nameof(GameComponentUtility.GameComponentTick))),
                };
                PatchedStages = 0;
                InstallStatus = JawaBenchTpsInstall.Run(targets, (name, m) =>
                {
                    var hooks = map[name];
                    h.Patch((MethodInfo)m, prefix: new HarmonyMethod(t.GetMethod(hooks[0], BindingFlags.Static | BindingFlags.NonPublic)),
                            finalizer: new HarmonyMethod(t.GetMethod(hooks[1], BindingFlags.Static | BindingFlags.NonPublic)));
                    PatchedStages++;
                }, () => { h.UnpatchAll(HarmonyId); PatchedStages = 0; }, out InstallDetail);
                if (InstallStatus == "failed") { InstallError = InstallDetail; return; }
                if (InstallStatus == "partial") InstallError = InstallDetail;
                Calibrate();
                Installed = true;
            }
            catch (Exception e)
            {
                InstallError = e.GetType().Name + ": " + e.Message;
                InstallStatus = "failed";
                Rollback();
            }
        }

        internal static void Rollback()
        {
            try { new Harmony(HarmonyId).UnpatchAll(HarmonyId); } catch { }
            Installed = false;
            PatchedStages = 0;
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
        // original returned or threw and, on the installed Harmony 2.4.x, leaves the original exception to be
        // rethrown unchanged - so a throwing tick no longer leaves a timer open, and we never swallow the game's
        // exception. TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS: the per-invocation start time, stage category and tick
        // id ride in the guard Scope (__state), never in a static; the THREAD is checked before anything else is
        // touched (TickBegin and the tick id used to be written first); a nested DoSingleTick is REJECTED (it would
        // overwrite the outer tick's stage baseline) and counted; a finalizer whose prefix never ran (late install,
        // skipped prefix) records nothing and is counted. Our own failures are CONTAINED: any exception in a hook
        // disables attribution and is reported; none escapes into the tick.
        internal static volatile bool Disabled;
        internal static string RuntimeError;
        internal static int MainThreadId = -1;
        internal static readonly JawaBenchHookGuard GTick = new JawaBenchHookGuard("DoSingleTick", false);
        internal static readonly JawaBenchHookGuard GStage = new JawaBenchHookGuard("stages", true);
        internal static JawaBenchHookGuard[] Guards => new[] { GTick, GStage };

        private static bool OnMain() { try { return UnityData.IsInMainThread; } catch { return false; } }

        private static void Fail(string where, Exception e)
        {
            try { GStage.Fault(where, e); } catch { }
            if (Disabled) return;
            Disabled = true;
            RuntimeError = where + ": " + e.GetType().Name + ": " + e.Message;
        }

        private static void Begin(int phase, int cat, out JawaBenchHookGuard.Scope s)
        {
            s = default(JawaBenchHookGuard.Scope);
            if (Disabled) { s.Rejected = true; return; }
            try
            {
                if (!GStage.TryEnter(OnMain(), out s)) { Stages.CountSkip(); return; }
                s.I0 = cat;
                WD.Enter(phase);
                s.I1 = 1;    // phase entered
                s.T0 = Stopwatch.GetTimestamp();
            }
            catch (Exception e) { Fail("stage-begin", e); }
        }

        private static void End(JawaBenchHookGuard.Scope s)
        {
            try
            {
                if (!GStage.Exit(s)) { if (!s.Rejected && !Disabled) Stages.CountSkip(); return; }
                if (s.I1 == 1) WD.Exit();
                if (!Disabled && s.T0 > 0) Stages.End(s.I0, s.T0, Stopwatch.GetTimestamp());
            }
            catch (Exception e) { Fail("stage-end", e); }
        }

        private static void TickPre(TickManager __instance, out JawaBenchHookGuard.Scope __state)
        {
            __state = default(JawaBenchHookGuard.Scope);
            if (Disabled) { __state.Rejected = true; return; }
            try
            {
                // thread and nesting FIRST: nothing below runs for a foreign thread or a nested tick
                if (!GTick.TryEnter(OnMain(), out __state)) { Stages.CountSkip(); return; }
                Stages.TickBegin();
                __state.I0 = __instance != null ? __instance.TicksGame + 1 : -1;   // DoSingleTick increments first
                WD.Enter(WD.PTick);
                __state.I1 = 1;
                __state.T0 = Stopwatch.GetTimestamp();
            }
            catch (Exception e) { Fail("tick-prefix", e); }
        }

        private static void TickFin(JawaBenchHookGuard.Scope __state, Exception __exception)
        {
            try
            {
                if (!GTick.Exit(__state)) { if (!__state.Rejected && !Disabled) Stages.CountSkip(); return; }
                if (__exception != null) GTick.NoteThrew();
                if (__state.I1 == 1) WD.Exit();
                if (!Disabled && __state.T0 > 0) Stages.TickEnd(__state.T0, Stopwatch.GetTimestamp(), __state.I0);
            }
            catch (Exception e) { Fail("tick-finalizer", e); }
        }

        private static int TlCat(TickList l)
        {
            switch (_tickType(l)) { case TickerType.Rare: return CRare; case TickerType.Long: return CLong; default: return CNormal; }
        }

        private static void TlPre(TickList __instance, out JawaBenchHookGuard.Scope __state)
        {
            __state = default(JawaBenchHookGuard.Scope);
            if (Disabled) { __state.Rejected = true; return; }
            int c;
            try { c = TlCat(__instance); }      // pure field read; the category is captured ONCE, here, for the finalizer
            catch (Exception e) { Fail("tl-prefix", e); __state.Rejected = true; return; }
            Begin(WD.PTlNormal + c - CNormal, c, out __state);
        }

        private static void TlFin(JawaBenchHookGuard.Scope __state) { End(__state); }

        private static void WorldPre(out JawaBenchHookGuard.Scope __state) { Begin(WD.PWorld, CWorld, out __state); }
        private static void WorldFin(JawaBenchHookGuard.Scope __state) { End(__state); }
        private static void WorldPostPre(out JawaBenchHookGuard.Scope __state) { Begin(WD.PWorldPost, CWorldPost, out __state); }
        private static void WorldPostFin(JawaBenchHookGuard.Scope __state) { End(__state); }
        private static void MapPrePre(out JawaBenchHookGuard.Scope __state) { Begin(WD.PMapPre, CMapPre, out __state); }
        private static void MapPreFin(JawaBenchHookGuard.Scope __state) { End(__state); }
        private static void MapPostPre(out JawaBenchHookGuard.Scope __state) { Begin(WD.PMapPost, CMapPost, out __state); }
        private static void MapPostFin(JawaBenchHookGuard.Scope __state) { End(__state); }
        private static void MapCompPre(out JawaBenchHookGuard.Scope __state) { Begin(WD.PMapComp, CMapComp, out __state); }
        private static void MapCompFin(JawaBenchHookGuard.Scope __state) { End(__state); }
        private static void GameCompPre(out JawaBenchHookGuard.Scope __state) { Begin(WD.PGameComp, CGameComp, out __state); }
        private static void GameCompFin(JawaBenchHookGuard.Scope __state) { End(__state); }

        /// <summary>This window's attribution as JSON fields (no braces), then reset. Main thread.</summary>
        internal static string TakeWindowFields()
        {
            if (!Installed) return "\"attr\":null";
            if (Disabled) return "\"attr\":null,\"attrError\":" + JawaBenchTpsMath.Json(RuntimeError);
            return Stages.TakeWindowFields(CostPerPairSeconds);
        }
    }
}
