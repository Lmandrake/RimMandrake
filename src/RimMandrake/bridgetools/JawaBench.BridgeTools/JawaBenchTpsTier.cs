// JawaBenchTpsTier.cs - the TPS record's TEST TIER (telemetry design P2, owner picks Q3a + Q4a, 2026-10-11):
// Transient/weekly_cleaning_2026-10-11/08_telemetry_deep_design.md sections 2-3.
//
// ARMED PER TEST by whoever holds the bridge: jawa/telemetry_tier tier=test ttl_min=60 (cap 240). While armed:
//   T0  per tick (JawaBenchTpsStages.TickEnd -> JawaBenchTpsTierCore.TickTier): tick-duration histogram + flight ring.
//       Needs the attribution profiler (its DoSingleTick hook is the tick clock); attribution off = no T0, said in status.
//   T1  1 s sample windows instead of 5 s; each `sample` row gains hist/histV, exc, br, and every row carries `tier`.
//   Flight dumps on: incident (gap > 2 s), a tick > 250 ms, > 50 log calls in a window, jawa/telemetry_mark dump=true,
//       and disarm. One per 30 s; the main thread copies the ring into a pooled buffer and the EXISTING writer thread
//       writes tps\flight\flight_<session>_<seq>.jsonl.gz (format: JawaBenchTpsTierCore.cs header) + a `flight` row.
//   Log counter: Harmony PREFIXES on Verse.Log.Error(string), ErrorOnce(string,int), Warning(string),
//       WarningOnce(string,int), Message(string) (signatures read from decompiled 1.6 via RimSage 2026-10-11). Each
//       runs BEFORE the method's own `if (PreventLogging) return;`, so calls the 10,000-message cap suppresses are
//       counted (exc.sup: reachedMaxMessagesLimit or logDisablers > 0 at the call). A thread-static depth guard counts
//       only the OUTERMOST log call (ErrorOnce -> Error, our own logging) - nested calls are not double counted. An
//       ErrorOnce/WarningOnce whose key is already in Log.usedKeys writes nothing and is counted only as exc.rep. The
//       exception-burst trigger compares e + w (errors + warnings), never messages or once-repeats.
//       Still blind: direct UnityEngine.Debug.LogError and unhandled Unity exceptions.
//   Bridge occupancy: prefix+finalizer on RimBridgeServer.RimBridgeMainThread.Pump and RimBridgeAsyncScheduler.Pump
//       (both called from RimBridgeServer's Root.Update postfix; decompiled from the installed RimBridgeServer.dll
//       2026-10-11). Every [Tool] body runs on the main thread inside RimBridgeAsyncScheduler.Pump (the extension
//       provider wraps each invocation in RimBridgeAsyncScheduler.RunAsync), and every ctx.MainThread.InvokeAsync body
//       inside RimBridgeMainThread.Pump - so the two pumps ARE the choke point. br.calls = work items present when a
//       pump started (a LOWER bound: items enqueued during the pump also run in it; one tool call is usually 2-3 items),
//       br.mainMs = main-thread ms inside both pumps (all bridge work, not only JawaBench's), br.qMaxMs = the longest
//       wait of the async scheduler's queue (first enqueue -> the pump that drained it). The InvokeAsync queue's wait
//       is NOT measured: its enqueue is inline in a generic method.
// Hooks are installed at the FIRST arm only, so a session that never arms has no tier patch at all; while disarmed every
// hook body returns at its first volatile read. Campaign never runs T0/T1: the tool is in the campaign-denied test-only
// family, and an armed tier disarms itself the frame the effective profile reads campaign.
// Each piece has its own switch in tps_settings.json: histogram, flight, excCounter, bridgeOccupancy.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Threading;
using HarmonyLib;
using Verse;
using C = JawaBench.BridgeTools.JawaBenchTpsTierCore;
using M = JawaBench.BridgeTools.JawaBenchTpsMath;
using W = JawaBench.BridgeTools.JawaBenchTpsWriter;
using WD = JawaBench.BridgeTools.JawaBenchTpsWatchdog;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchTpsTier
    {
        internal static readonly C.ExcCounter Exc = new C.ExcCounter();
        internal static readonly C.TickTier Tick = new C.TickTier(Stopwatch.Frequency) { Exc = Exc };
        internal static readonly C.BridgeOcc Br = new C.BridgeOcc();
        internal static readonly C.FlightGate Gate = new C.FlightGate();
        internal static readonly C.SnapPool Pool = new C.SnapPool(C.RingTicks);

        internal static volatile bool Armed;
        private static volatile bool _excOn, _brOn;
        private static bool _histOn;
        private static double _until;
        private static string _by, _why, _armedUtc;
        private static int _dumpSeq;
        internal static long Dumps, DumpErrors, DumpRefused, FirstSights, ExcFileDropped, HookFaults, Arms;
        private static long _excFileBytes = -1;
        internal static string LastDump, LastDumpStatus, LastDisarm;

        internal const string LogHarmonyId = "mandrake.jawabench.tps.tier.log", BrHarmonyId = "mandrake.jawabench.tps.tier.br";
        internal static string LogHookStatus = "not-installed", LogHookDetail, BrHookStatus = "not-installed", BrHookDetail;
        private static bool _hooksTried;
        private static FieldInfo _reachedMax, _disablers, _usedKeys;
        private static ICollection _mtPending, _asPending;

        [ThreadStatic] private static int _logDepth;

        internal static string TierName => Armed ? C.TierTest : C.TierCampaign;

        // ------------------------------------------------------------------ arm / disarm (main thread)
        internal static object Arm(double ttlMin, string by, string why)
        {
            if (!JawaBenchTpsSampler.Installed || !W.Running)
                return new { success = false, error = "TPS sampler not running (" + (JawaBenchTpsSampler.InstallError ?? JawaBenchTpsSampler.InstallStatus) + "): nothing to arm" };
            double ttl = C.ClampTtl(ttlMin);
            double now = WD.Now;
            bool renew = Armed;
            _until = now + ttl * 60.0;
            _by = by; _why = why;
            if (!renew)
            {
                var st = JawaBenchTpsSampler.Settings;
                InstallHooks();
                _histOn = st.Histogram;
                Tick.HistOn = st.Histogram;
                Tick.FlightOn = st.Flight;
                if (st.Flight) Tick.Allocate();
                Tick.Clear();
                Gate.Reset();
                long ignored;
                Exc.TakeFields(out ignored);        // a fresh window: nothing counted before the arm
                Br.TakeFields(Stopwatch.Frequency);
                Interlocked.Exchange(ref Br.FirstEnqueue, 0);
                _excOn = st.ExcCounter && LogHookStatus != "failed" && LogHookStatus != "not-installed";
                _brOn = st.BridgeOccupancy && BrHookStatus != "failed" && BrHookStatus != "not-installed";
                JawaBenchTpsProfiler.Stages.Tier = Tick;
                Tick.On = (st.Histogram || st.Flight) && JawaBenchTpsProfiler.Installed;
                _armedUtc = W.Utc();
                Armed = true;
                Arms++;
                JawaBenchTpsSampler.SetCadence(C.TestCadenceSeconds);
            }
            W.Enqueue("marker", "\"why\":" + W.Json(renew ? "tier-renew" : "tier-arm") + ",\"tier\":\"test\",\"ttlMin\":" + M.F(ttl, 1) +
                                ",\"by\":" + W.Json(by) + ",\"note\":" + W.Json(why) + ",\"t0\":" + (Tick.On ? "true" : "false") +
                                ",\"histogram\":" + B(_histOn && Tick.On) + ",\"flight\":" + B(Tick.FlightOn && Tick.On) +
                                ",\"excCounter\":" + B(_excOn) + ",\"bridgeOccupancy\":" + B(_brOn) +
                                ",\"histV\":" + C.Hist.Version + ",\"histEdgesMs\":" + C.Hist.EdgesJson() +
                                ",\"logHooks\":" + W.Json(LogHookStatus) + ",\"brHooks\":" + W.Json(BrHookStatus));
            return Status(true);
        }

        internal static object Disarm(string reason)
        {
            if (!Armed) return Status(true);
            string dump = Dump(C.TrigDisarm);     // while the ring still holds the test; bypasses the 30 s limit
            Tick.On = false;
            _excOn = false;
            _brOn = false;
            Armed = false;
            LastDisarm = reason;
            JawaBenchTpsSampler.SetCadence(M.CadenceSeconds);
            W.Enqueue("marker", "\"why\":\"tier-disarm\",\"tier\":\"campaign\",\"reason\":" + W.Json(reason) + ",\"dump\":" + W.Json(dump) +
                                ",\"ticksRecorded\":" + Tick.Recorded + ",\"dumps\":" + Dumps + ",\"dumpsSuppressed\":" + Gate.Suppressed);
            return Status(true);
        }

        /// <summary>Every frame (sampler's Root.Update finalizer, main thread): TTL, profile, and pending dump triggers.</summary>
        internal static void Frame(double now)
        {
            if (!Armed) return;
            if (now >= _until) { Disarm("ttl"); return; }
            var pol = JawaBenchCompanionSafety.CurrentPolicy;
            if (pol != null && pol.Name == JawaBenchSafetyCore.Campaign) { Disarm("profile-campaign"); return; }
            string p = Tick.PendingTrigger;
            if (p != null) { Tick.PendingTrigger = null; Dump(p); }
        }

        internal static void RequestDump(string trigger)
        {
            if (Armed && Tick.PendingTrigger == null) Tick.PendingTrigger = trigger;
        }

        /// <summary>The tier fields every `sample` row carries (no leading comma). Main thread, at window close.</summary>
        internal static string WindowFields()
        {
            if (!Armed) return "\"tier\":\"campaign\"";
            var sb = new System.Text.StringBuilder(400).Append("\"tier\":\"test\"");
            if (_histOn && Tick.On) sb.Append(',').Append(C.Hist.TakeFields(Tick.HistCounts));
            if (_excOn)
            {
                long errWarn;
                sb.Append(',').Append(Exc.TakeFields(out errWarn));
                if (errWarn > C.ExcBurst) RequestDump(C.TrigExc);
            }
            if (_brOn) sb.Append(',').Append(Br.TakeFields(Stopwatch.Frequency));
            return sb.ToString();
        }

        // ------------------------------------------------------------------ flight dump (main thread copies, writer writes)
        /// <summary>fired | rate-limited | not-armed | flight-off | empty | pool-exhausted | writer-refused</summary>
        internal static string Dump(string trigger)
        {
            string r = DumpInner(trigger);
            LastDumpStatus = trigger + ": " + r;
            return r;
        }

        private static string DumpInner(string trigger)
        {
            if (!Armed) return "not-armed";
            if (!Tick.FlightOn || !Tick.Allocated || !Tick.On) return "flight-off";
            if (Tick.Count == 0) return "empty";
            int suppressed;
            if (trigger == C.TrigDisarm) suppressed = Gate.SuppressedSinceLast;     // the end-of-test ring is never rate-limited away
            else if (!Gate.TryFire(WD.Now, out suppressed)) return "rate-limited";
            var snap = Pool.Rent();
            if (snap == null)
            {
                DumpRefused++;
                W.Enqueue("flight", "\"file\":null,\"trigger\":" + W.Json(trigger) + ",\"error\":\"pool exhausted: two dumps still being written\"");
                return "pool-exhausted";
            }
            Tick.CopyTo(snap);
            int seq = ++_dumpSeq;
            string session = JawaBenchTpsSampler.Session, utc = W.Utc();
            string dir = Path.Combine(JawaBenchTpsSampler.RecordDir, "flight");
            string name = C.FlightFileName(session, seq);
            double freq = Stopwatch.Frequency;
            bool queued = W.EnqueueSide(() =>
            {
                try
                {
                    string path = Path.Combine(dir, name);
                    string header = C.FlightHeader(session, seq, trigger, utc, snap, freq);
                    long bytes = C.WriteFlightFile(path, header, snap);
                    int deleted = C.EnforceFlightCap(dir, path, C.FlightDirCapBytes);
                    int w = snap.Worst();
                    Dumps++;
                    LastDump = name;
                    W.Enqueue("flight", "\"file\":" + W.Json(name) + ",\"trigger\":" + W.Json(trigger) + ",\"flightSeq\":" + seq +
                                        ",\"tickFrom\":" + snap.TickFrom + ",\"tickTo\":" + snap.TickTo + ",\"ticks\":" + snap.Count +
                                        ",\"worstDurUs\":" + (w < 0 ? 0 : snap.Dur[w]) + ",\"worstTg\":" + (w < 0 ? -1 : snap.Tg[w]) +
                                        ",\"bytes\":" + bytes + ",\"suppressedBefore\":" + suppressed + ",\"dirDeleted\":" + deleted +
                                        ",\"error\":null");
                }
                catch (Exception e)
                {
                    DumpErrors++;
                    W.Enqueue("flight", "\"file\":" + W.Json(name) + ",\"trigger\":" + W.Json(trigger) + ",\"flightSeq\":" + seq +
                                        ",\"error\":" + W.Json(e.GetType().Name + ": " + e.Message));
                }
                finally { Pool.Return(snap); }
            });
            if (!queued)
            {
                Pool.Return(snap);
                DumpRefused++;
                W.Enqueue("flight", "\"file\":null,\"trigger\":" + W.Json(trigger) + ",\"error\":\"writer refused the side job\"");
                return "writer-refused";
            }
            return "fired";
        }

        // ------------------------------------------------------------------ hooks (installed at the first arm)
        private static void InstallHooks()
        {
            if (_hooksTried) return;
            _hooksTried = true;
            try
            {
                _reachedMax = AccessTools.Field(typeof(Log), "reachedMaxMessagesLimit");
                _disablers = AccessTools.Field(typeof(Log), "logDisablers");
                _usedKeys = AccessTools.Field(typeof(Log), "usedKeys");
                var h = new Harmony(LogHarmonyId);
                var t = typeof(JawaBenchTpsTier);
                Func<string, HarmonyMethod> hm = n => new HarmonyMethod(t.GetMethod(n, BindingFlags.Static | BindingFlags.NonPublic));
                var targets = new List<JawaBenchTpsInstall.Target>
                {
                    new JawaBenchTpsInstall.Target("Log.Error", true, () => AccessTools.Method(typeof(Log), nameof(Log.Error), new[] { typeof(string) })),
                    new JawaBenchTpsInstall.Target("Log.ErrorOnce", false, () => AccessTools.Method(typeof(Log), nameof(Log.ErrorOnce), new[] { typeof(string), typeof(int) })),
                    new JawaBenchTpsInstall.Target("Log.Warning", false, () => AccessTools.Method(typeof(Log), nameof(Log.Warning), new[] { typeof(string) })),
                    new JawaBenchTpsInstall.Target("Log.WarningOnce", false, () => AccessTools.Method(typeof(Log), nameof(Log.WarningOnce), new[] { typeof(string), typeof(int) })),
                    new JawaBenchTpsInstall.Target("Log.Message", false, () => AccessTools.Method(typeof(Log), nameof(Log.Message), new[] { typeof(string) })),
                };
                LogHookStatus = JawaBenchTpsInstall.Run(targets, (name, m) =>
                {
                    string pre = name == "Log.Error" ? nameof(ErrPre) : name == "Log.ErrorOnce" ? nameof(ErrOncePre) : name == "Log.Warning" ? nameof(WarnPre)
                               : name == "Log.WarningOnce" ? nameof(WarnOncePre) : nameof(MsgPre);
                    h.Patch((MethodInfo)m, prefix: hm(pre), finalizer: hm(nameof(LogFin)));
                }, () => h.UnpatchAll(LogHarmonyId), out LogHookDetail);
            }
            catch (Exception e) { LogHookStatus = "failed"; LogHookDetail = e.GetType().Name + ": " + e.Message; try { new Harmony(LogHarmonyId).UnpatchAll(LogHarmonyId); } catch { } }
            try
            {
                var mt = AccessTools.TypeByName("RimBridgeServer.RimBridgeMainThread");
                var asy = AccessTools.TypeByName("RimBridgeServer.RimBridgeAsyncScheduler");
                if (mt != null) _mtPending = AccessTools.Field(mt, "Pending")?.GetValue(null) as ICollection;
                if (asy != null) _asPending = AccessTools.Field(asy, "Pending")?.GetValue(null) as ICollection;
                var h = new Harmony(BrHarmonyId);
                var t = typeof(JawaBenchTpsTier);
                Func<string, HarmonyMethod> hm = n => new HarmonyMethod(t.GetMethod(n, BindingFlags.Static | BindingFlags.NonPublic));
                var targets = new List<JawaBenchTpsInstall.Target>
                {
                    new JawaBenchTpsInstall.Target("RimBridgeMainThread.Pump", true, () => mt == null ? null : AccessTools.Method(mt, "Pump", Type.EmptyTypes)),
                    new JawaBenchTpsInstall.Target("RimBridgeAsyncScheduler.Pump", true, () => asy == null ? null : AccessTools.Method(asy, "Pump", Type.EmptyTypes)),
                    new JawaBenchTpsInstall.Target("RimBridgeAsyncScheduler.Enqueue", false, () => asy == null ? null : AccessTools.Method(asy, "Enqueue")),
                };
                BrHookStatus = JawaBenchTpsInstall.Run(targets, (name, m) =>
                {
                    if (name == "RimBridgeMainThread.Pump") h.Patch((MethodInfo)m, prefix: hm(nameof(MtPumpPre)), finalizer: hm(nameof(PumpFin)));
                    else if (name == "RimBridgeAsyncScheduler.Pump") h.Patch((MethodInfo)m, prefix: hm(nameof(AsPumpPre)), finalizer: hm(nameof(PumpFin)));
                    else h.Patch((MethodInfo)m, prefix: hm(nameof(AsEnqPre)));
                }, () => h.UnpatchAll(BrHarmonyId), out BrHookDetail);
                if (_mtPending == null || _asPending == null) BrHookDetail += "; a Pending queue was not readable: calls undercounted";
            }
            catch (Exception e) { BrHookStatus = "failed"; BrHookDetail = e.GetType().Name + ": " + e.Message; try { new Harmony(BrHarmonyId).UnpatchAll(BrHarmonyId); } catch { } }
        }

        // ---- Verse.Log prefixes (ANY thread). __state = this call was counted (and owns the depth guard).
        private static void ErrPre(string text, out bool __state) { __state = Enter(C.ExcCounter.LError, text, null); }
        private static void ErrOncePre(string text, int key, out bool __state) { __state = Enter(OnceUsed(key) ? C.ExcCounter.LOnceRepeat : C.ExcCounter.LErrorOnce, text, key); }
        private static void WarnPre(string text, out bool __state) { __state = Enter(C.ExcCounter.LWarning, text, null); }
        private static void WarnOncePre(string text, int key, out bool __state) { __state = Enter(OnceUsed(key) ? C.ExcCounter.LOnceRepeat : C.ExcCounter.LWarningOnce, text, key); }

        /// <summary>Vanilla's ErrorOnce/WarningOnce write nothing for a key already in Log.usedKeys. Read without logLock
        /// (racy: a stale answer misfiles one call), and only when the counter is on.</summary>
        private static bool OnceUsed(int key)
        {
            if (!_excOn || _logDepth > 0 || _usedKeys == null) return false;
            try { var hs = _usedKeys.GetValue(null) as HashSet<int>; return hs != null && hs.Contains(key); }
            catch { return false; }
        }
        private static void MsgPre(string text, out bool __state) { __state = Enter(C.ExcCounter.LMessage, text, null); }
        private static void LogFin(bool __state) { if (__state) _logDepth--; }

        private static bool Enter(char level, string text, int? key)
        {
            if (!_excOn || _logDepth > 0) return false;     // off, or nested inside a counted log call
            _logDepth++;
            try { Count(level, text, key); }
            catch { Interlocked.Increment(ref HookFaults); }
            return true;
        }

        private static void Count(char level, string text, int? key)
        {
            if (level == C.ExcCounter.LOnceRepeat) { if (key.HasValue) Exc.NoteRepeat(key.Value); else Exc.Note(level, null, false); return; }
            bool sup = false;
            try
            {
                if (_reachedMax != null && (bool)_reachedMax.GetValue(null)) sup = true;
                else if (_disablers != null && (int)_disablers.GetValue(null) > 0) sup = true;
            }
            catch { }
            string sig = C.ExcCounter.Signature(level, text, key);
            if (!Exc.Note(level, sig, sup)) return;
            Interlocked.Increment(ref FirstSights);
            string line = C.ExcCounter.FirstSightLine(W.Utc(), JawaBenchTpsSampler.Session, level, sig, key, sup, WD.LastTicksGame,
                                                      text, Environment.StackTrace);
            string path = Path.Combine(Path.Combine(JawaBenchTpsSampler.RecordDir, "exc"), "exc_" + JawaBenchTpsSampler.Session + ".jsonl");
            if (!W.EnqueueSide(() => AppendExc(path, line))) Interlocked.Increment(ref ExcFileDropped);
        }

        /// <summary>Writer thread: append one first-sight line, capped at ExcFileCapBytes per session file.</summary>
        private static void AppendExc(string path, string line)
        {
            byte[] b = System.Text.Encoding.UTF8.GetBytes(line + "\n");
            if (_excFileBytes < 0) _excFileBytes = File.Exists(path) ? new FileInfo(path).Length : 0;
            if (_excFileBytes + b.Length > C.ExcFileCapBytes) { ExcFileDropped++; return; }
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            W.AppendImpl(path, b, b.Length);
            _excFileBytes += b.Length;
        }

        // ---- RimBridgeServer pumps (main thread: RimBridgeServer's Root.Update postfix). __state = start timestamp, 0 = off.
        private static void MtPumpPre(out long __state)
        {
            __state = 0;
            if (!_brOn) return;
            try
            {
                if (_mtPending != null) Br.Calls += _mtPending.Count;
                __state = Stopwatch.GetTimestamp();
            }
            catch { Interlocked.Increment(ref HookFaults); }
        }

        private static void AsPumpPre(out long __state)
        {
            __state = 0;
            if (!_brOn) return;
            try
            {
                long now = Stopwatch.GetTimestamp();
                if (_asPending != null) Br.Calls += _asPending.Count;
                long first = Interlocked.Exchange(ref Br.FirstEnqueue, 0);
                if (first > 0 && now - first > Br.QMaxTicks) Br.QMaxTicks = now - first;
                __state = now;
            }
            catch { Interlocked.Increment(ref HookFaults); }
        }

        private static void PumpFin(long __state)
        {
            if (__state <= 0) return;
            try { long d = Stopwatch.GetTimestamp() - __state; if (d > 0) Br.MainTicks += d; }
            catch { Interlocked.Increment(ref HookFaults); }
        }

        private static void AsEnqPre()
        {
            if (!_brOn) return;
            try { Interlocked.CompareExchange(ref Br.FirstEnqueue, Stopwatch.GetTimestamp(), 0); }
            catch { }
        }

        // ------------------------------------------------------------------ status (for the tools)
        internal static object Status(bool success)
        {
            double left = Armed ? Math.Max(0, _until - WD.Now) : 0;
            return new
            {
                success,
                tier = TierName,
                armedUtc = Armed ? _armedUtc : null,
                minutesLeft = Armed ? Math.Round(left / 60.0, 2) : 0,
                by = Armed ? _by : null,
                why = Armed ? _why : null,
                lastDisarm = LastDisarm,
                windowSeconds = Armed ? C.TestCadenceSeconds : M.CadenceSeconds,
                t0 = new { on = Tick.On, histogram = _histOn && Tick.On, flight = Tick.FlightOn && Tick.On, ticksRecorded = Tick.Recorded,
                           ringTicks = Tick.Count, ringCapacity = Tick.Capacity, needsAttribution = !JawaBenchTpsProfiler.Installed },
                flight = new { dumps = Dumps, errors = DumpErrors, refused = DumpRefused, suppressed = Gate.Suppressed, last = LastDump, lastStatus = LastDumpStatus },
                exc = new { on = _excOn, total = Exc.Total, firstSights = Interlocked.Read(ref FirstSights), excFileDropped = Interlocked.Read(ref ExcFileDropped),
                            hooks = LogHookStatus, detail = LogHookDetail },
                bridge = new { on = _brOn, hooks = BrHookStatus, detail = BrHookDetail },
                hookFaults = Interlocked.Read(ref HookFaults),
                writerSide = new { depth = W.SideDepth, refused = W.SideRefused, errors = W.SideErrors, lastError = W.SideLastError },
            };
        }

        private static string B(bool b) => b ? "true" : "false";
    }
}
