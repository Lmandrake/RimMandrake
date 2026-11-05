// JawaBenchAllocProbe.cs - jawa/alloc_probe (MONO_ALLOC_MEASURE_PER_TICK_ON_GAME): on the game's own Mono,
//   calibrate  judge each allocation counter against a known allocation (JawaBenchAllocCore.Calibrate): the per-thread
//              GC.GetAllocatedBytesForCurrentThread, the all-thread GC.GetTotalMemory(false) and Unity's
//              Profiler.GetMonoUsedSizeLong; plus the control rate (other threads' allocation while this one idles), the
//              Unity version and the GC mode. Patches nothing.
//   start      for N minutes (default 10, max 60), meter every concrete MapComponentTick / GameComponentTick /
//              WorldComponentTick override and TickList.Tick (by tick type), plus an optional exact list of extra methods
//              (inclusive: they nest inside a component's row), with the trusted heap counter; count game ticks
//              (DoSingleTick) and record every GC landing per frame (Root.Update), with the system running when the count
//              moved and any GC.Collect call since the previous frame (its caller). TEST profile only (it patches methods).
//   read       the calibration, the per-system table (bytes/tick, sorted), the landings and the trigger line.
//   stop       hooks inert at once (patches stay: unpatching an executing hot method is the hazard).
// Every hook is main-thread only, allocation-free on the hot path, and turns itself off after a fault.

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using HarmonyLib;
using RimBridgeServer.Sdk;
using RimWorld.Planet;
using UnityEngine.Scripting;
using Verse;
using A = JawaBench.BridgeTools.JawaBenchAllocCore;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchAllocProbe
    {
        internal const string HarmonyId = "mandrake.jawabench.allocprobe";
        internal const int MaxTargets = 600, MaxLandings = 400;
        private static readonly object Gate = new object();
        private static Harmony _harmony;
        private static readonly HashSet<MethodBase> _patched = new HashSet<MethodBase>();
        private static volatile Dictionary<MethodBase, int> _map;
        private static string[] _keys = new string[0];
        private static A.Meter[] _meters = new A.Meter[0];
        private static int _tickListBase = -1;                         // TickList rows: base + (int)tickType
        private static AccessTools.FieldRef<TickList, TickerType> _tickType;
        private static readonly A.Meter TickMeter = new A.Meter();
        private static long _gameTicks, _untilTs = long.MinValue, _startTs;
        private static volatile bool _on;
        internal static string Status = "never started", LastFault, StartedUtc;
        private static readonly List<string> Refused = new List<string>(), ExplicitHooks = new List<string>();
        private static long _faults, _foreign, _explicitCalls;
        private static bool _explicitHooked;                           // every GC.Collect overload hooked (CollectIncremental is extern: incremental, never a full pause)

        private static bool Reserved(MethodBase mb) =>
            mb.DeclaringType == typeof(GC) || mb.DeclaringType == typeof(GarbageCollector)
            || mb.DeclaringType?.Assembly == typeof(JawaBenchAllocProbe).Assembly || mb.DeclaringType?.Assembly == typeof(Harmony).Assembly   // our hooks' own code: re-entry
            || mb == AccessTools.Method(typeof(TickManager), "DoSingleTick") || mb == AccessTools.Method(typeof(Root), nameof(Root.Update));

        // landings (main thread)
        private static readonly List<A.Landing> Landings = new List<A.Landing>(MaxLandings);   // never grows inside a hook
        private static int _lastGc;
        private static long _lastHeap, _lastFrameTs, _heapAfterPrevGc;
        private static string _hostKey, _pendingExplicit;
        private static double _hostMs;

        // calibration
        internal static readonly List<A.Calibration> Cals = new List<A.Calibration>();
        internal static string Trusted;
        private static Func<long> _count;                              // the trusted counter the meters read
        internal static double ControlPerSw;                           // bytes per Stopwatch tick, other threads
        private static readonly object[] Sink = new object[Math.Max(A.LargeCount, A.SmallCount)];
        private static readonly Func<long> ThreadAlloc = Bind();
        private static readonly Func<long> Heap = () => GC.GetTotalMemory(false);
        private static readonly Func<long> MonoUsed = () => UnityEngine.Profiling.Profiler.GetMonoUsedSizeLong();
        private static readonly string[] Order = { "gcTotalMemory", "monoUsedSize", "threadAlloc" };

        private static Func<long> Bind()
        {
            try
            {
                MethodInfo mi = typeof(GC).GetMethod("GetAllocatedBytesForCurrentThread", Type.EmptyTypes);
                return mi == null ? null : (Func<long>)Delegate.CreateDelegate(typeof(Func<long>), mi);
            }
            catch (Exception) { return null; }
        }

        internal static bool Running => _on && Stopwatch.GetTimestamp() < Interlocked.Read(ref _untilTs);
        private static int Gc() => GC.CollectionCount(0);
        private static bool Mono => Type.GetType("Mono.Runtime") != null;

        // ---------------- calibrate ----------------
        /// <summary>Null on success; refuses during a window (its allocations and a counter switch would contaminate it).</summary>
        internal static string Calibrate(int trials)
        {
            if (Running) return "refused: a window is running (stop it first)";
            Cals.Clear();
            bool mono = Mono;
            int n = Math.Max(A.MinTrials, Math.Min(trials, 25));
            var probes = new[]
            {
                new { name = "large", payload = A.LargePayload, count = A.LargeCount },
                new { name = "small", payload = A.SmallPayload, count = A.SmallCount },
                new { name = "1MB", payload = 1 << 20, count = 1 },
            };
            var instruments = new[] { new { name = "threadAlloc", f = ThreadAlloc }, new { name = "gcTotalMemory", f = Heap }, new { name = "monoUsedSize", f = SafeMonoUsed() } };
            foreach (var ins in instruments)
                foreach (var p in probes)
                {
                    int payload = p.payload, count = p.count;
                    Action<bool> alloc = real =>
                    {
                        if (real) for (int i = 0; i < count; i++) Sink[i] = new byte[payload];
                        else for (int i = 0; i < count; i++) Sink[i] = null;
                    };
                    var c = A.Calibrate(ins.name, p.name, ins.f, Gc, alloc, count * A.ObjectBytes(payload, mono), n, n * 3);
                    Array.Clear(Sink, 0, Sink.Length);
                    Cals.Add(c);
                }
            Trusted = A.Trusted(Cals, Order);
            _count = Trusted == "gcTotalMemory" ? Heap : Trusted == "monoUsedSize" ? SafeMonoUsed() : Trusted == "threadAlloc" ? ThreadAlloc : null;
            // control rate: this thread spins 5 ms allocating nothing; the trusted counter's change is other threads'
            var rates = new List<long>();
            Func<long> ctl = _count ?? Heap;
            for (int i = 0; i < 9; i++)
            {
                int g0 = Gc();
                long h0 = ctl(), t0 = Stopwatch.GetTimestamp(), spin = 0;
                while (Stopwatch.GetTimestamp() - t0 < Stopwatch.Frequency / 200) spin++;
                long dt = Stopwatch.GetTimestamp() - t0, dh = ctl() - h0;
                if (Gc() == g0 && dt > 0) rates.Add((long)(Math.Max(0, dh) * 1000000.0 / dt));
            }
            ControlPerSw = rates.Count == 0 ? double.NaN : A.Median(rates) / 1000000.0;
            return null;
        }

        private static Func<long> SafeMonoUsed()
        {
            try { MonoUsed(); return MonoUsed; } catch (Exception) { return null; }
        }

        // ---------------- start / stop ----------------
        internal static string Start(string extra, double minutes)
        {
            lock (Gate)
            {
                if (!UnityData.IsInMainThread) return "refused: start only from the main thread";
                var pol = JawaBenchCompanionSafety.PolicyNow();
                if (pol.Name != JawaBenchSafetyCore.Test) return "refused: alloc_probe patches methods at runtime, a test-profile act; the " + pol.Name + " profile does not allow it";
                if (Running) return "refused: a window is already running (stop it first)";
                if (Cals.Count == 0) Calibrate(9);
                if (Trusted == null || _count == null) return "refused: no heap counter passed calibration (" + string.Join("; ", Cals.Select(c => c.Render())) + ")";
                var map = new Dictionary<MethodBase, int>();
                var keys = new List<string>();
                var refused = new List<string>();
                void Add(MethodBase mb, string key)
                {
                    if (mb == null || map.ContainsKey(mb) || mb.IsAbstract || mb.GetMethodBody() == null) return;
                    if (keys.Count >= MaxTargets) { refused.Add(key + ": over " + MaxTargets); return; }
                    map[mb] = keys.Count; keys.Add(key);
                }
                foreach (var (bt, name) in new[] { (typeof(MapComponent), "MapComponentTick"), (typeof(GameComponent), "GameComponentTick"), (typeof(WorldComponent), "WorldComponentTick") })
                    foreach (Type t in GenTypes.AllSubclasses(bt))      // abstract intermediates too: an override declared there runs for its children
                    {
                        MethodInfo mi = null;
                        try { mi = t.GetMethod(name, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly, null, Type.EmptyTypes, null); } catch { }
                        if (mi != null) Add(mi, t.FullName + ":" + name);
                    }
                MethodInfo tl = AccessTools.Method(typeof(TickList), "Tick");
                int tlBase = keys.Count;
                if (tl != null)
                {
                    map[tl] = tlBase;
                    foreach (TickerType tt in Enum.GetValues(typeof(TickerType))) keys.Add("TickList.Tick[" + tt + "]");
                }
                if (!string.IsNullOrWhiteSpace(extra))
                    foreach (var raw in extra.Split(';'))
                    {
                        var s = raw.Trim();
                        int c = s.LastIndexOf(':');
                        if (c <= 0) { refused.Add(s + ": not Ns.Type:Method"); continue; }
                        Type t = AccessTools.TypeByName(s.Substring(0, c));
                        var cands = t == null ? new List<MethodInfo>() : t.GetMethods(BindingFlags.DeclaredOnly | BindingFlags.Instance | BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic)
                            .Where(m => m.Name == s.Substring(c + 1) && !m.IsGenericMethodDefinition).ToList();
                        if (cands.Count != 1) { refused.Add(s + (t == null ? ": type not found" : ": " + cands.Count + " overloads")); continue; }
                        if (Reserved(cands[0])) { refused.Add(s + ": reserved (the probe's own hooks, the companion, Harmony or GC.Collect)"); continue; }
                        Add(cands[0], s + " (inclusive)");
                    }
                try
                {
                    _tickType = AccessTools.FieldRefAccess<TickList, TickerType>("tickType");
                    if (_harmony == null) _harmony = new Harmony(HarmonyId);
                    _on = false;
                    _meters = keys.Select(_ => new A.Meter()).ToArray();
                    _keys = keys.ToArray();
                    _tickListBase = tl != null ? tlBase : -1;
                    _map = map;
                    var self = typeof(JawaBenchAllocProbe);
                    HarmonyMethod H(string n) => new HarmonyMethod(self.GetMethod(n, BindingFlags.Static | BindingFlags.NonPublic));
                    foreach (var mb in map.Keys)
                        if (!_patched.Contains(mb))
                        {
                            try { _harmony.Patch(mb, prefix: H(nameof(Pre)), finalizer: H(nameof(Fin))); _patched.Add(mb); }
                            catch (Exception e) { refused.Add(mb.DeclaringType?.FullName + ":" + mb.Name + ": patch failed " + e.GetType().Name); }
                        }
                    // the tick count and the frame-level GC observation are the window: without either there is no table and no trigger
                    if (!PatchOnce(AccessTools.Method(typeof(TickManager), "DoSingleTick"), H(nameof(TickPre)), H(nameof(TickFin)), "DoSingleTick", refused)
                        | !PatchOnce(AccessTools.Method(typeof(Root), nameof(Root.Update)), null, H(nameof(FrameFin)), "Root.Update", refused))
                    {
                        Status = "failed: a required hook did not install (" + string.Join("; ", refused) + ")";
                        return Status;
                    }
                    ExplicitHooks.Clear();
                    _explicitHooked = true;
                    foreach (var mi in typeof(GC).GetMethods(BindingFlags.Public | BindingFlags.Static).Where(m => m.Name == "Collect"))
                    {
                        bool ok = PatchOnce(mi, H(nameof(CollectPre)), null, null, null);
                        _explicitHooked &= ok;
                        ExplicitHooks.Add("GC.Collect(" + mi.GetParameters().Length + ")" + (ok ? "" : " UNHOOKED"));
                    }
                    foreach (var mi in typeof(GarbageCollector).GetMethods(BindingFlags.Public | BindingFlags.Static).Where(m => m.Name == "CollectIncremental"))
                        ExplicitHooks.Add("GarbageCollector.CollectIncremental" + (PatchOnce(mi, H(nameof(CollectPre)), null, null, null) ? "" : " UNHOOKED (extern)"));
                }
                catch (Exception e) { _on = false; Status = "failed: " + e.GetType().Name + ": " + e.Message; return Status; }
                Refused.Clear(); Refused.AddRange(refused);
                foreach (var m in _meters) m.Clear();
                TickMeter.Clear();
                Landings.Clear();
                _gameTicks = 0; _faults = 0; _foreign = 0; _explicitCalls = 0; LastFault = null;
                _lastGc = Gc(); _lastHeap = _heapAfterPrevGc = Heap(); _lastFrameTs = Stopwatch.GetTimestamp();
                _hostKey = null; _pendingExplicit = null; _hostMs = 0;
                double mins = double.IsNaN(minutes) || minutes <= 0 ? 10 : Math.Min(minutes, 60);
                _startTs = Stopwatch.GetTimestamp();
                Interlocked.Exchange(ref _untilTs, _startTs + (long)(mins * 60 * Stopwatch.Frequency));
                StartedUtc = DateTime.UtcNow.ToString("o");
                Status = "running";
                _on = true;
                return null;
            }
        }

        private static bool PatchOnce(MethodBase mb, HarmonyMethod pre, HarmonyMethod fin, string name, List<string> refused)
        {
            if (mb == null) { refused?.Add(name + ": not found"); return false; }
            if (_patched.Contains(mb)) return true;
            try { _harmony.Patch(mb, prefix: pre, finalizer: fin); _patched.Add(mb); return true; }
            catch (Exception e) { refused?.Add(name + ": patch failed " + e.GetType().Name); return false; }
        }

        internal static void Stop() { _on = false; Interlocked.Exchange(ref _untilTs, long.MinValue); Status = "stopped"; }

        private struct St { internal int Idx; internal int G0; internal long H0, T0; internal bool Valid; }

        private static bool Live()
        {
            if (!_on) return false;
            if (Stopwatch.GetTimestamp() >= Interlocked.Read(ref _untilTs)) { _on = false; Status = "expired"; return false; }
            if (!UnityData.IsInMainThread) { Interlocked.Increment(ref _foreign); return false; }
            return true;
        }

        private static void Pre(MethodBase __originalMethod, object __instance, out St __state)
        {
            __state = default(St);
            try
            {
                if (!Live()) return;
                var map = _map;
                if (map == null || !map.TryGetValue(__originalMethod, out int idx)) return;
                if (idx == _tickListBase && __instance is TickList t) idx += (int)_tickType(t);
                __state.Idx = idx; __state.G0 = Gc(); __state.H0 = _count(); __state.Valid = true;
                __state.T0 = Stopwatch.GetTimestamp();
            }
            catch (Exception e) { Fault("prefix", e); }
        }

        private static void Fin(St __state)
        {
            try
            {
                if (!__state.Valid) return;
                long t1 = Stopwatch.GetTimestamp();
                long h1 = _count();
                bool gc = Gc() != __state.G0;
                var ms = _meters;
                if (__state.Idx < ms.Length)
                {
                    ms[__state.Idx].Add(h1 - __state.H0, t1 - __state.T0, gc);
                    if (gc && _hostKey == null) { _hostKey = _keys[__state.Idx]; _hostMs = (t1 - __state.T0) * 1000.0 / Stopwatch.Frequency; }
                }
            }
            catch (Exception e) { Fault("finalizer", e); }
        }

        private static void TickPre(out St __state)
        {
            __state = default(St);
            try
            {
                if (!Live()) return;
                __state.G0 = Gc(); __state.H0 = _count(); __state.Valid = true; __state.T0 = Stopwatch.GetTimestamp();
            }
            catch (Exception e) { Fault("tick prefix", e); }
        }

        private static void TickFin(St __state)
        {
            try
            {
                if (!__state.Valid) return;
                long t1 = Stopwatch.GetTimestamp();
                bool gc = Gc() != __state.G0;
                TickMeter.Add(_count() - __state.H0, t1 - __state.T0, gc);
                _gameTicks++;
                if (gc && _hostKey == null) { _hostKey = "tick:other"; _hostMs = (t1 - __state.T0) * 1000.0 / Stopwatch.Frequency; }
            }
            catch (Exception e) { Fault("tick finalizer", e); }
        }

        private static void FrameFin()
        {
            try
            {
                if (!Live()) return;
                long now = Stopwatch.GetTimestamp();
                long heap = Heap();
                int g = Gc();
                if (g != _lastGc && Landings.Count < MaxLandings)
                {
                    Landings.Add(new A.Landing
                    {
                        Tick = Find.TickManager?.TicksGame ?? -1, Count = g - _lastGc,
                        FrameMs = (now - _lastFrameTs) * 1000.0 / Stopwatch.Frequency,
                        Host = _hostKey, HostMs = _hostMs, HeapBefore = _lastHeap, HeapAfter = heap,
                        AllocSincePrev = _lastHeap - _heapAfterPrevGc, ExplicitCaller = _pendingExplicit,
                    });
                    _heapAfterPrevGc = heap;
                }
                if (g != _lastGc) { _hostKey = null; _hostMs = 0; }
                _pendingExplicit = null;   // GC.Collect is synchronous: a call whose frame saw no collection collected nothing
                _lastGc = g; _lastHeap = heap; _lastFrameTs = Stopwatch.GetTimestamp();
            }
            catch (Exception e) { Fault("frame", e); }
        }

        private static void CollectPre()
        {
            try
            {
                if (!_on) return;
                Interlocked.Increment(ref _explicitCalls);
                if (!Live()) { _pendingExplicit = "(foreign thread)"; return; }   // still explicit, caller not walked off-thread
                string who = "?";
                var st = new StackTrace(1, false);                       // allocates: acceptable, a full collection follows at once
                for (int i = 0; i < st.FrameCount; i++)
                {
                    var m = st.GetFrame(i)?.GetMethod();
                    var t = m?.DeclaringType;
                    if (t == null || t == typeof(JawaBenchAllocProbe) || t == typeof(GC) || t == typeof(GarbageCollector)) continue;
                    string ns = t.Namespace ?? "";
                    if (ns.StartsWith("HarmonyLib") || t.FullName.Contains("DMD<")) continue;
                    who = t.FullName + ":" + m.Name; break;
                }
                _pendingExplicit = who;
            }
            catch (Exception) { _pendingExplicit = "?"; }
        }

        private static void Fault(string where, Exception e)
        {
            Interlocked.Increment(ref _faults);
            try { LastFault = where + ": " + e.GetType().Name + ": " + e.Message; } catch { }
            _on = false; Status = "disabled after a fault";
        }

        // ---------------- read ----------------
        internal static object Report(int top)
        {
            double f = Stopwatch.Frequency;
            var rows = new List<KeyValuePair<double, string>>();
            for (int i = 0; i < _keys.Length && i < _meters.Length; i++)
            {
                var m = _meters[i];
                if (m.Calls == 0) continue;
                double bpt = _gameTicks == 0 || m.ByteCalls == 0 ? 0 : m.Bytes * ((double)m.Calls / m.ByteCalls) / _gameTicks;
                rows.Add(new KeyValuePair<double, string>(bpt, A.Row(_keys[i], m, _gameTicks, ControlPerSw, f)));
            }
            var sorted = rows.OrderByDescending(kv => kv.Key).Select(kv => kv.Value).ToList();
            var shown = sorted.Take(Math.Max(1, top)).Concat(sorted.Skip(Math.Max(1, top)).Where(r => r.StartsWith("RimMandrake") || r.StartsWith("JawaBench"))).ToList();
            string S(Func<string> g) { try { return g(); } catch (Exception e) { return "unavailable: " + e.GetType().Name; } }
            return new
            {
                status = Running ? "running" : Status, startedUtc = StartedUtc,
                windowSeconds = _startTs == 0 ? 0 : Math.Round((Stopwatch.GetTimestamp() - _startTs) / f, 1),
                unityVersion = S(() => UnityEngine.Application.unityVersion), gcMode = S(() => GarbageCollector.GCMode.ToString()),
                gcIncremental = S(() => GarbageCollector.isIncremental ? "true" : "false"),
                incrementalSliceNs = S(() => GarbageCollector.incrementalTimeSliceNanoseconds.ToString()),
                mono = Mono, calibration = Cals.Select(c => c.Render()).ToArray(), trusted = Trusted,
                controlBytesPerMs = A.F(ControlPerSw * f / 1000.0, 1),
                gameTicks = _gameTicks, tick = A.Row("DoSingleTick", TickMeter, _gameTicks, ControlPerSw, f),
                systems = shown.ToArray(), systemsMetered = _keys.Length, systemsWithCalls = rows.Count,
                landings = Landings.Select(A.RenderLanding).ToArray(), trigger = A.Trigger(Landings, _explicitHooked), explicitHooked = _explicitHooked,
                explicitHooks = ExplicitHooks.ToArray(), explicitCalls = Interlocked.Read(ref _explicitCalls),
                refused = Refused.ToArray(), foreignThreadCalls = Interlocked.Read(ref _foreign),
                faults = Interlocked.Read(ref _faults), lastFault = LastFault,
            };
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/alloc_probe",
            Description =
                "Allocation and GC probe on the game's Mono (MONO_ALLOC_MEASURE_PER_TICK_ON_GAME). action=calibrate judges " +
                "GC.GetAllocatedBytesForCurrentThread, GC.GetTotalMemory and Profiler.GetMonoUsedSizeLong against known " +
                "allocations (PASS within 10%, BLIND, OFF, UNMEASURED; patches nothing). action=start meters bytes/tick per " +
                "component tick and tick list with the trusted counter for N minutes and records every GC landing per frame " +
                "(host system, heap, explicit GC.Collect caller); TEST profile only. action=read reports; stop makes the hooks inert.",
            ResultDescription = "success, probe (calibration, trusted, systems, landings, trigger, ...).")]
        public static async Task<object> AllocProbe(
            IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "calibrate | start | read | stop", DefaultValue = "read")] string action = "read",
            [ToolParameter(Description = "start: extra exact methods 'Ns.Type:Method;...' (inclusive rows)", DefaultValue = null)] string extra = null,
            [ToolParameter(Description = "start: minutes (default 10, max 60)", DefaultValue = 10)] double minutes = 10,
            [ToolParameter(Description = "calibrate: GC-free trials per probe (5-25, default 9)", DefaultValue = 9)] int trials = 9,
            [ToolParameter(Description = "read: rows shown besides our own (default 40)", DefaultValue = 40)] int top = 40)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var a = (action ?? "read").Trim().ToLowerInvariant();
                if (a == "calibrate")
                {
                    var why = JawaBenchAllocProbe.Calibrate(trials);
                    if (why != null) return Fail(why, JawaBenchAllocProbe.Report(top));
                }
                else if (a == "start")
                {
                    var why = JawaBenchAllocProbe.Start(extra, minutes);
                    if (why != null) return Fail(why, JawaBenchAllocProbe.Report(top));
                }
                else if (a == "stop") JawaBenchAllocProbe.Stop();
                else if (a != "read") return Fail("action must be calibrate, start, read or stop");
                return new { success = true, probe = JawaBenchAllocProbe.Report(top) };
            }, cancellationToken).ConfigureAwait(false);
        }
    }
}
