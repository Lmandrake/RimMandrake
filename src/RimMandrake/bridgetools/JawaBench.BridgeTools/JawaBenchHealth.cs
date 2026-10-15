// JawaBenchHealth.cs - the game-health metrics, the Verse half: the hooks that FEED JawaBenchHealthCore.
//
// Spec + ledger: design/RimMandrake/game_health_record.md. Metric ids (each with its own switch in
// <SaveData>/JawaBench/tps/health_settings.json and `jawa/health action=switch`):
//   tps.frame-hist            interval between successive Root.Update prefixes -> fh-v1 histogram, one window a minute
//   spike.gc-timing           GC.CollectionCount(0) delta per frame; a >=250 ms gap with a delta is a COINCIDENCE
//   tps.log-counts            Application.logMessageReceivedThreaded counts + Verse.Log cap/logger/lock state
//   tps.bridge-occupancy      RimBridgeServer's main-thread pumps: busy time (interval union) + queue-delay upper bound
//   tps.capability-inventory  read-only: engine/Harmony/GC identity, ProfilerRecorder counters probed, source states
//   opt.profiler              (JawaBenchHealthProfiler below) on demand, expiring, exact allowlist; preset "own" is the
//                             merged opt.own-counters
//
// NOTHING HERE IS ALWAYS-ON. game_health_record.md: nothing heavier goes always-on until the TPS full-list overhead
// test (MUST 17) passes. Every hook is installed only by `jawa/health action=arm` (TTL, default 30 min, max 240) and
// goes INERT at expiry or `disarm` (one comparison per call). Patches are not removed at disarm: repatching an
// executing hot method is the hazard GPT review 1.5 names; installing them is the same act the TPS sampler already
// performs at registration (it patches Root.Update from inside Root.Update's postfix).
// ⛔ This file does not touch the TPS sampler's files: separate Harmony id, separate guards, separate settings.
//
// ENGINE MEMBERS, READ FROM DECOMPILED SOURCES 2026-10-14 (never guessed):
//   Verse/Log.cs (RimSage)   private static int messageCount; private static bool reachedMaxMessagesLimit;
//                            private static int logDisablers (LockMessages); const StopLoggingAtMessageCount = 10000;
//                            Notify_MessageReceivedThreadedInternal sets Debug.unityLogger.logEnabled = false at the cap
//   RimWorld/VersionControl  public static string CurrentVersionStringWithRev
//   UnityEngine.CoreModule   (ilspycmd) Application.logMessageReceivedThreaded (LogCallback), Application.unityVersion,
//                            Logger.logEnabled, Unity.Profiling.ProfilerRecorder.StartNew(ProfilerCategory, string, int,
//                            ProfilerRecorderOptions) / Valid / Count / LastValue / Start / Dispose, ProfilerCategory.Memory
//                            and .Render, UnityEngine.Scripting.GarbageCollector.GCMode / isIncremental
//   RimBridgeServer.dll      (ilspycmd, workshop 3727949765) internal static class RimBridgeServer.RimBridgeMainThread:
//                            public static void Pump(); private static readonly Queue<IMainThreadWorkItem> Pending.
//                            internal static class RimBridgeServer.RimBridgeAsyncScheduler: Pump() (called twice per
//                            frame); private static readonly Queue<QueuedContinuation> Pending. Both pumped from the
//                            server's Root_Update_Patch postfix. Third-party private names: a rename makes the source
//                            "unavailable" by name, never a silent zero.
//
// HOOK LAWS (TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS; JawaBenchHookGuard): thread check and nesting check before any
// state is touched; per-invocation values live in the Scope the prefix hands its own finalizer; finalizers are void
// (the game's exception propagates unchanged); every body is try/catch -> guard Fault (visible, disables that hook).
// The log handler runs on ANY thread: it only does Interlocked increments and never logs (logging inside it recurses).

using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Text;
using HarmonyLib;
using Unity.Profiling;
using UnityEngine;
using Verse;
using H = JawaBench.BridgeTools.JawaBenchHealthCore;
using W = JawaBench.BridgeTools.JawaBenchTpsWriter;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchHealth
    {
        internal const string HarmonyId = "mandrake.jawabench.health";
        internal const double DefaultArmMinutes = 30, MaxArmMinutes = 240, WindowSeconds = 60;
        internal static readonly double Freq = Stopwatch.Frequency;

        internal static H.Switches Sw = new H.Switches();
        internal static string SettingsPath;
        internal static readonly Dictionary<string, H.Meter> Meters = new Dictionary<string, H.Meter>();
        internal static readonly JawaBenchHookGuard GRoot = new JawaBenchHookGuard("health.Root.Update", false);
        internal static readonly JawaBenchHookGuard GPump = new JawaBenchHookGuard("health.bridge-pump", false);

        // arm state (monotonic seconds)
        internal static readonly H.Expiry Arm = new H.Expiry();
        internal static string ArmedBy, ArmedAtUtc, InstallStatus = "not installed (arm installs)", InstallDetail;
        private static bool _installed;
        private static Harmony _harmony;
        private static readonly object Gate = new object();
        private static volatile bool _live;                 // armed and unexpired: the hooks' one cheap check
        private static volatile bool _onFrame, _onGc, _onLog, _onOcc;
        internal static double NowS => Stopwatch.GetTimestamp() / Freq;

        // tps.frame-hist + spike.gc-timing (main thread only: GRoot rejects foreign threads)
        internal static readonly H.HistRing Ring = new H.HistRing(240);
        internal static H.FrameHist Window = new H.FrameHist(), Session = new H.FrameHist();
        internal static double WindowStartS = double.NaN, SessionStartS = double.NaN;
        private static long _lastFrameTs = -1;
        private static int _lastGc = -1;
        internal static readonly H.GapGc Gc = new H.GapGc();

        // tps.log-counts (process-scoped: never reset at a game change)
        internal static readonly H.LogTally Logs = new H.LogTally();
        internal static readonly H.ResetTracker CapResets = new H.ResetTracker();
        internal static string LogCountingSinceUtc;
        private static bool _logSubscribed;
        private static FieldInfo _fCount, _fReached, _fDisablers;

        // tps.bridge-occupancy
        internal const int PumpMain = 0, PumpAsync = 1;
        internal static readonly H.Occupancy Occ = new H.Occupancy(2);
        internal static double OccSinceS = double.NaN;
        internal static string PumpStatus = "not installed";
        private static MethodBase _pumpMain, _pumpAsync;
        private static FieldInfo _pendingMain, _pendingAsync;

        static JawaBenchHealth()
        {
            foreach (var id in H.MetricIds) Meters[id] = new H.Meter();
            _mFrame = Meters[H.MFrameHist]; _mGc = Meters[H.MGc]; _mLog = Meters[H.MLogCounts]; _mOcc = Meters[H.MBridgeOcc];
        }
        private static readonly H.Meter _mFrame, _mGc, _mLog, _mOcc;

        private static bool OnMain() { try { return UnityData.IsInMainThread; } catch { return false; } }

        internal static void RefreshFlags()
        {
            _onFrame = Sw.On(H.MFrameHist); _onGc = Sw.On(H.MGc); _onLog = Sw.On(H.MLogCounts); _onOcc = Sw.On(H.MBridgeOcc);
        }

        internal static bool Live => _live && Arm.Live(NowS);

        // ------------------------------------------------------------------ arm / disarm (main thread, from the tool)
        internal static string ArmNow(double minutes, string by)
        {
            lock (Gate)
            {
                if (!OnMain()) return "refused: arm only from the main thread";
                if (!_installed)
                {
                    try { LoadSwitches(); } catch (Exception e) { Sw = new H.Switches { Note = "settings read failed: " + e.GetType().Name }; }
                    RefreshFlags();
                    InstallHooks(by);
                    _installed = true;
                }
                if (InstallStatus == "failed") return "not armed: install failed (" + InstallDetail + ")";
                double m = Arm.Set(NowS, minutes, DefaultArmMinutes, MaxArmMinutes);
                ArmedBy = by; ArmedAtUtc = DateTime.UtcNow.ToString("o");
                _lastFrameTs = -1; _lastGc = -1;                        // never span a frame interval across an unarmed stretch
                if (double.IsNaN(SessionStartS)) SessionStartS = NowS;
                if (double.IsNaN(OccSinceS)) OccSinceS = NowS;
                WindowStartS = NowS;
                SubscribeLog();
                _live = true;
                return "armed for " + m + " min";
            }
        }

        internal static void Disarm()
        {
            lock (Gate)
            {
                _live = false;
                Arm.Clear();
                CloseWindow(NowS);
                UnsubscribeLog();
                JawaBenchHealthCapabilities.StopProbe();
            }
        }

        private static void LoadSwitches()
        {
            var dir = Path.Combine(Path.Combine(GenFilePaths.SaveDataFolderPath, "JawaBench"), "tps");
            SettingsPath = Path.Combine(dir, "health_settings.json");
            if (!File.Exists(SettingsPath))
            {
                Directory.CreateDirectory(dir);
                var sb = new StringBuilder("{");
                for (int i = 0; i < H.MetricIds.Length; i++) sb.Append(i == 0 ? "" : ", ").Append(H.J(H.MetricIds[i])).Append(": true");
                File.WriteAllText(SettingsPath, sb.Append("}\n").ToString());
            }
            Sw = H.Switches.Parse(File.ReadAllText(SettingsPath));
        }

        private static void InstallHooks(string by)
        {
            try { _harmony = new Harmony(HarmonyId); }
            catch (Exception e) { InstallStatus = "failed"; InstallDetail = "Harmony ctor: " + e.Message; return; }
            var self = typeof(JawaBenchHealth);
            HarmonyMethod Hm(string n) => n == null ? null : new HarmonyMethod(self.GetMethod(n, BindingFlags.Static | BindingFlags.NonPublic));
            Type tMain = null, tAsync = null;
            try { tMain = AccessTools.TypeByName("RimBridgeServer.RimBridgeMainThread"); } catch { }
            try { tAsync = AccessTools.TypeByName("RimBridgeServer.RimBridgeAsyncScheduler"); } catch { }
            _pumpMain = tMain == null ? null : AccessTools.Method(tMain, "Pump", Type.EmptyTypes);
            _pumpAsync = tAsync == null ? null : AccessTools.Method(tAsync, "Pump", Type.EmptyTypes);
            _pendingMain = tMain == null ? null : AccessTools.Field(tMain, "Pending");
            _pendingAsync = tAsync == null ? null : AccessTools.Field(tAsync, "Pending");
            var plan = new List<JawaBenchTpsInstall.Target>
            {
                new JawaBenchTpsInstall.Target("Root.Update", true, () => AccessTools.Method(typeof(Root), nameof(Root.Update))),
                new JawaBenchTpsInstall.Target("RimBridgeMainThread.Pump", false, () => _pumpMain),
                new JawaBenchTpsInstall.Target("RimBridgeAsyncScheduler.Pump", false, () => _pumpAsync),
            };
            string detail;
            InstallStatus = JawaBenchTpsInstall.Run(plan, (name, m) =>
            {
                if (name == "Root.Update") _harmony.Patch((MethodBase)m, prefix: Hm(nameof(RootPrefix)));
                else _harmony.Patch((MethodBase)m, prefix: Hm(nameof(PumpPrefix)), finalizer: Hm(nameof(PumpFinalizer)));
            }, () => _harmony.UnpatchAll(HarmonyId), out detail);
            InstallDetail = detail + " (by " + by + ")";
            PumpStatus = _pumpMain == null && _pumpAsync == null
                ? "unavailable: RimBridgeServer pump methods not found by name (renamed upstream?)"
                : InstallStatus == "failed" ? "failed" : (_pumpMain != null && _pumpAsync != null ? "installed" : "partial: " + detail);
            try { _fCount = AccessTools.Field(typeof(Log), "messageCount"); } catch { }
            try { _fReached = AccessTools.Field(typeof(Log), "reachedMaxMessagesLimit"); } catch { }
            try { _fDisablers = AccessTools.Field(typeof(Log), "logDisablers"); } catch { }
        }

        // ------------------------------------------------------------------ Root.Update prefix: frame-hist + gc-timing
        private static void RootPrefix()
        {
            try
            {
                if (!GRoot.TryEnter(OnMain(), out var scope)) return;
                try
                {
                    if (!_live) return;
                    long now = Stopwatch.GetTimestamp();
                    double nowS = now / Freq;
                    if (!Arm.Live(nowS)) { _live = false; CloseWindow(nowS); return; }
                    if (_lastFrameTs >= 0)
                    {
                        double ms = (now - _lastFrameTs) * 1000.0 / Freq;
                        if (_onFrame)
                        {
                            if (nowS - WindowStartS >= WindowSeconds) CloseWindow(nowS);
                            Window.Add(ms); Session.Add(ms);
                        }
                        long t1 = Stopwatch.GetTimestamp();
                        if (_onFrame) _mFrame.Add(t1 - now);
                        if (_onGc)
                        {
                            int gc = GC.CollectionCount(0);
                            int d = _lastGc >= 0 ? gc - _lastGc : 0;
                            _lastGc = gc;
                            Gc.Observe(ms, d, nowS);
                            _mGc.Add(Stopwatch.GetTimestamp() - t1);
                        }
                    }
                    else if (_onGc) _lastGc = GC.CollectionCount(0);
                    _lastFrameTs = now;
                }
                finally { GRoot.Exit(scope); }          // prefix-only hook: the scope closes here, not in a finalizer
            }
            catch (Exception e) { try { GRoot.Fault("health-root", e); } catch { } }
        }

        /// <summary>Close the current minute window into the ring and write one TPS-record row (kind "health").
        /// Main thread. Allocates once a minute, never per frame.</summary>
        internal static void CloseWindow(double nowS)
        {
            try
            {
                if (double.IsNaN(WindowStartS)) return;
                var w = Window;
                Window = new H.FrameHist();
                double start = WindowStartS;
                WindowStartS = nowS;
                if (w.N == 0 && w.Rejected == 0) return;
                Ring.Close(w, start, nowS);
                var cap = ReadCap();
                W.Enqueue("health", "\"metric\":\"health.window\",\"windowS\":" + H.F(nowS - start) +
                                    ",\"frameHist\":" + (_onFrame ? w.Json() : H.Reading.SwitchedOff().Json()) +
                                    ",\"gc\":" + H.J(_onGc ? Gc.Text() : "off") +
                                    ",\"log\":" + H.J(_onLog ? H.LogLine(Logs, cap) : "off") + ",\"logState\":" + H.J(cap.Word) +
                                    ",\"bridgeBusyMs\":" + (_onOcc ? H.F(Occ.BusyTicks * 1000.0 / Freq) : "null"));
            }
            catch (Exception e) { try { GRoot.Fault("health-window", e); } catch { } }
        }

        // ------------------------------------------------------------------ log counts
        private static void SubscribeLog()
        {
            if (_logSubscribed) return;
            try { Application.logMessageReceivedThreaded += OnLog; _logSubscribed = true; LogCountingSinceUtc = DateTime.UtcNow.ToString("o"); }
            catch { }
        }

        private static void UnsubscribeLog()
        {
            if (!_logSubscribed) return;
            try { Application.logMessageReceivedThreaded -= OnLog; } catch { }
            _logSubscribed = false;
        }

        /// <summary>ANY thread. Interlocked only; never logs (that would recurse into this handler).</summary>
        private static void OnLog(string condition, string stackTrace, LogType type)
        {
            try
            {
                if (!_onLog || !_live) return;
                long t0 = Stopwatch.GetTimestamp();
                Logs.Note((int)type);
                _mLog.Add(Stopwatch.GetTimestamp() - t0);
            }
            catch { }
        }

        /// <summary>Read the four engine facts separately; an unreadable one is null, never a default.</summary>
        internal static H.CapState ReadCap()
        {
            int? count = null, dis = null; bool? reached = null, enabled = null;
            try { if (_fCount != null) count = (int)_fCount.GetValue(null); } catch { }
            try { if (_fReached != null) reached = (bool)_fReached.GetValue(null); } catch { }
            try { if (_fDisablers != null) dis = (int)_fDisablers.GetValue(null); } catch { }
            try { enabled = UnityEngine.Debug.unityLogger.logEnabled; } catch { }
            if (count.HasValue) CapResets.Observe(count.Value);
            return H.JudgeCap(count, reached, dis, enabled);
        }

        // ------------------------------------------------------------------ bridge pumps
        private static int Pending(FieldInfo f)
        {
            try { return f?.GetValue(null) is ICollection c ? c.Count : -1; } catch { return -1; }   // unlocked read: approximate
        }

        private static void PumpPrefix(MethodBase __originalMethod, out JawaBenchHookGuard.Scope __state)
        {
            __state = default(JawaBenchHookGuard.Scope);
            try
            {
                if (!GPump.TryEnter(OnMain(), out __state)) return;
                __state.I0 = -1;                 // until fully set up: a fault below must not record a bogus interval
                long t0 = Stopwatch.GetTimestamp();
                if (!_live || !_onOcc) { __state.I0 = -1; return; }
                bool main = __originalMethod == _pumpMain;
                __state.I0 = main ? PumpMain : PumpAsync;
                __state.I1 = Pending(main ? _pendingMain : _pendingAsync);
                long t1 = Stopwatch.GetTimestamp();
                __state.T0 = t1;                 // the pump body starts after our prefix work
                __state.T1 = t1 - t0;            // our prefix cost
            }
            catch (Exception e) { try { GPump.Fault("health-pump-prefix", e); } catch { } }
        }

        private static void PumpFinalizer(JawaBenchHookGuard.Scope __state, Exception __exception)
        {
            try
            {
                long end = Stopwatch.GetTimestamp();
                if (!__state.Valid) { GPump.Exit(__state); return; }
                GPump.Exit(__state);
                if (__exception != null) GPump.NoteThrew();
                if (__state.I0 < 0) return;
                Occ.Note(__state.I0, __state.T0, end, Math.Max(0, __state.I1));
                _mOcc.Add(__state.T1 + (Stopwatch.GetTimestamp() - end));
            }
            catch (Exception e) { try { GPump.Fault("health-pump-finalizer", e); } catch { } }
        }

        // ------------------------------------------------------------------ readings for the tool
        internal static H.Reading SourceReading(string id)
        {
            if (!Sw.On(id)) return H.Reading.SwitchedOff();
            if (!_installed) return H.Reading.Unavailable("not installed: jawa/health action=arm installs and arms");
            if (InstallStatus == "failed") return H.Reading.Failed(InstallDetail);
            if (id == H.MBridgeOcc && !PumpStatus.StartsWith("installed") && !PumpStatus.StartsWith("partial")) return H.Reading.Unavailable(PumpStatus);
            if (id == H.MLogCounts && !_logSubscribed) return H.Reading.Unavailable("log handler not subscribed (disarmed)");
            if (!Live) return H.Reading.Unavailable("installed but not armed (inert)");
            var m = Meters[id].MeanUs(Freq);
            return m.IsOk ? m : H.Reading.Unavailable("armed; no hook calls timed yet");
        }
    }
}
