// JawaBenchHealthProfiler.cs - opt.profiler (game_health_record.md), with opt.own-counters MERGED into it as the
// preset "own": an ON-DEMAND, EXPIRING timer on an EXACT allowlist of named methods. Also
// JawaBenchHealthCapabilities: the read-only tps.capability-inventory probe.
//
// Why the merge: "own counters" needs timers on our own mods' hot paths. Without editing (and redeploying) every mod,
// the only way to get them is a Harmony timer on a named list of our methods - which is exactly this profiler with a
// standing list. Keeping them as one mechanism means one switch, one hook pair and one cost to judge; the "own" preset
// is a list, not a second recorder. Neither is always-on (MUST 17 gate).
//
// LAWS (GPT review 1.5 and 4; game_health_record.md rules 1-2):
//   * EXACT names only ("Namespace.Type:Method"), max 32; a wildcard, a duplicate or a bad shape refuses the WHOLE
//     list; an overloaded name is refused rather than one overload picked; a name that does not resolve in the
//     running game is reported unavailable by name.
//   * TEST PROFILE ONLY. Patching arbitrary methods at runtime is a test-family act: in the campaign profile
//     (JawaBenchCompanionSafety.PolicyNow()) start is refused here, without editing the shared family list.
//   * Expiring: default 10 min, max 60. After expiry every hook returns after one timestamp compare; `stop` makes them
//     inert at once. Patches are not removed (repatching an executing hot method is the hazard GPT 1.5 names).
//   * Inclusive time of the OUTERMOST call per method per thread (recursion is not double-counted); callees are
//     inside it; Harmony's own dispatch is not. Foreign-thread calls are timed (thread-static depth) and counted.
//   * Cost and attribution are separate: the report names methods and their measured time, never a mod "to blame".

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using System.Threading;
using HarmonyLib;
using Unity.Profiling;
using UnityEngine;
using UnityEngine.Scripting;
using Verse;
using H = JawaBench.BridgeTools.JawaBenchHealthCore;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchHealthProfiler
    {
        internal const string HarmonyId = "mandrake.jawabench.health.prof";
        private static readonly object Gate = new object();
        private static Harmony _harmony;
        private static volatile Dictionary<MethodBase, int> _map;        // swapped whole, read lock-free
        private static readonly HashSet<MethodBase> _patched = new HashSet<MethodBase>();
        internal static H.Meter[] Meters = new H.Meter[0];
        internal static string[] Keys = new string[0];
        internal static readonly List<string> Refused = new List<string>();
        internal static long ForeignCalls, Faults;
        internal static string LastFault, StartedBy, StartedUtc, Preset, Status = "never started";
        private static long _untilTs = long.MinValue;                     // Stopwatch ticks
        private static volatile bool _on;
        internal static double Minutes;

        internal static bool Running => _on && Stopwatch.GetTimestamp() < Interlocked.Read(ref _untilTs);

        /// <summary>Main thread. Returns null on success, else why not (nothing patched).</summary>
        internal static string Start(string methods, string preset, double minutes, string by)
        {
            lock (Gate)
            {
                if (!UnityData.IsInMainThread) return "refused: start only from the main thread";
                if (!JawaBenchHealth.Sw.On(H.MProfiler)) return "refused: opt.profiler is switched off";
                var pol = JawaBenchCompanionSafety.PolicyNow();
                if (pol.Name != JawaBenchSafetyCore.Test) return "refused: the profiler patches named methods at runtime, a test-profile act; the " + pol.Name + " profile does not allow it";
                string spec = methods;
                if (!string.IsNullOrWhiteSpace(preset))
                {
                    if (preset.Trim().ToLowerInvariant() != "own") return "unknown preset '" + preset + "' (known: own)";
                    spec = H.OwnPreset + (string.IsNullOrWhiteSpace(methods) ? "" : ";" + methods);
                }
                var errors = new List<string>();
                var targets = H.ParseAllowlist(spec, H.MaxProfileTargets, errors);
                if (errors.Count > 0) return "allowlist refused: " + string.Join("; ", errors);

                var map = new Dictionary<MethodBase, int>();
                var keys = new List<string>();
                var refused = new List<string>();
                foreach (var t in targets)
                {
                    Type type = null;
                    try { type = AccessTools.TypeByName(t.Type); } catch { }
                    var cands = type == null ? new List<MethodInfo>() : type.GetMethods(BindingFlags.DeclaredOnly | BindingFlags.Instance | BindingFlags.Static |
                                                                                         BindingFlags.Public | BindingFlags.NonPublic)
                        .Where(mi => mi.Name == t.Method && !mi.IsAbstract && !mi.IsGenericMethodDefinition).ToList();
                    string why = H.ResolveVerdict(t.Key, type != null, cands.Count);
                    if (why != null) { refused.Add(why); continue; }
                    map[cands[0]] = keys.Count;
                    keys.Add(t.Key);
                }
                if (keys.Count == 0) return "nothing resolved: " + string.Join("; ", refused);
                try
                {
                    if (_harmony == null) _harmony = new Harmony(HarmonyId);
                    var self = typeof(JawaBenchHealthProfiler);
                    var pre = new HarmonyMethod(self.GetMethod(nameof(Pre), BindingFlags.Static | BindingFlags.NonPublic));
                    var fin = new HarmonyMethod(self.GetMethod(nameof(Fin), BindingFlags.Static | BindingFlags.NonPublic));
                    _on = false;                                           // inert while the map is swapped
                    Meters = keys.Select(_ => new H.Meter()).ToArray();
                    Keys = keys.ToArray();
                    _map = map;
                    foreach (var mb in map.Keys)
                        if (_patched.Add(mb)) _harmony.Patch(mb, prefix: pre, finalizer: fin);
                }
                catch (Exception e) { _on = false; Status = "failed: " + e.GetType().Name + ": " + e.Message; return Status; }
                Refused.Clear(); Refused.AddRange(refused);
                ForeignCalls = 0; Faults = 0; LastFault = null;
                Minutes = double.IsNaN(minutes) || minutes <= 0 ? H.DefaultProfileMinutes : Math.Min(minutes, H.MaxProfileMinutes);
                Interlocked.Exchange(ref _untilTs, Stopwatch.GetTimestamp() + (long)(Minutes * 60 * Stopwatch.Frequency));
                StartedBy = by; StartedUtc = DateTime.UtcNow.ToString("o"); Preset = preset;
                Status = "running";
                _on = true;
                return null;
            }
        }

        internal static void Stop() { _on = false; Interlocked.Exchange(ref _untilTs, long.MinValue); Status = "stopped"; }

        private static void Pre(MethodBase __originalMethod, out JawaBenchHookGuard.Scope __state)
        {
            __state = default(JawaBenchHookGuard.Scope);
            try
            {
                if (!_on) return;
                long t0 = Stopwatch.GetTimestamp();
                if (t0 >= Interlocked.Read(ref _untilTs)) { _on = false; Status = "expired"; return; }
                var map = _map;
                if (map == null || !map.TryGetValue(__originalMethod, out int idx)) return;
                __state.I0 = idx;
                __state.I1 = 1;                                   // depth entered: the finalizer must Exit
                __state.Valid = H.Depth.Enter(idx);               // outermost only is timed
                if (!UnityData.IsInMainThread) Interlocked.Increment(ref ForeignCalls);
                __state.T0 = Stopwatch.GetTimestamp();
            }
            catch (Exception e) { NoteFault("prefix", e); }
        }

        private static void Fin(JawaBenchHookGuard.Scope __state)
        {
            try
            {
                long end = Stopwatch.GetTimestamp();
                if (__state.I1 != 1) return;
                H.Depth.Exit(__state.I0);
                if (!__state.Valid) return;
                var ms = Meters;
                if (__state.I0 < ms.Length) ms[__state.I0].Add(end - __state.T0);
            }
            catch (Exception e) { NoteFault("finalizer", e); }
        }

        private static void NoteFault(string where, Exception e)
        {
            Interlocked.Increment(ref Faults);
            try { LastFault = where + ": " + e.GetType().Name + ": " + e.Message; } catch { }
            _on = false; Status = "disabled after a fault";
        }

        internal static object Report()
        {
            double f = Stopwatch.Frequency;
            var rows = new List<object>();
            for (int i = 0; i < Keys.Length && i < Meters.Length; i++)
            {
                var m = Meters[i];
                rows.Add(new
                {
                    method = Keys[i], calls = m.Calls, meanUs = m.MeanUs(f).Render(), maxUs = m.MaxUs(f).Render(),
                    totalMs = m.Calls == 0 ? null : (object)Math.Round(m.TotalMs(f), 3),
                });
            }
            return new
            {
                status = Running ? "running" : Status, startedBy = StartedBy, startedUtc = StartedUtc, preset = Preset, minutes = Minutes,
                measures = "inclusive time of the outermost call per method per thread; Harmony dispatch excluded; no cause is established",
                methods = rows, refused = Refused.ToArray(), foreignThreadCalls = Interlocked.Read(ref ForeignCalls),
                faults = Interlocked.Read(ref Faults), lastFault = LastFault, mergedFrom = H.MergedIds,
            };
        }
    }

    /// <summary>tps.capability-inventory: what this build can measure, and why the rest cannot. Read-only except
    /// for the ProfilerRecorder probe, which starts a few Unity recorders on `probe` and disposes them on probe_end /
    /// disarm (they own unmanaged resources).</summary>
    internal static class JawaBenchHealthCapabilities
    {
        private struct Probe { internal string Category, Name, Unit; internal bool Started; internal string Error; internal ProfilerRecorder Rec; }
        private static Probe[] _probes;
        internal static string ProbeStartedUtc;

        // GPT review 1.1: Unity 2022.3 documents the first four as release-player counters and GC Allocated In Frame
        // as NOT; that is exactly what the probe exists to confirm or refute in this player.
        private static readonly string[][] Wanted =
        {
            new[] { "Memory", "Total Used Memory", "bytes" }, new[] { "Memory", "GC Used Memory", "bytes" },
            new[] { "Memory", "GC Reserved Memory", "bytes" }, new[] { "Memory", "System Used Memory", "bytes" },
            new[] { "Memory", "GC Allocated In Frame", "bytes" },
            new[] { "Render", "Draw Calls Count", "count" }, new[] { "Render", "Batches Count", "count" }, new[] { "Render", "SetPass Calls Count", "count" },
        };

        internal static void StartProbe()
        {
            StopProbe();
            var list = new Probe[Wanted.Length];
            for (int i = 0; i < Wanted.Length; i++)
            {
                var p = new Probe { Category = Wanted[i][0], Name = Wanted[i][1], Unit = Wanted[i][2] };
                try
                {
                    var cat = p.Category == "Memory" ? ProfilerCategory.Memory : ProfilerCategory.Render;
                    p.Rec = ProfilerRecorder.StartNew(cat, p.Name, 1, ProfilerRecorderOptions.Default);
                    if (p.Rec.Valid && !p.Rec.IsRunning) p.Rec.Start();
                    p.Started = true;
                }
                catch (Exception e) { p.Error = e.GetType().Name + ": " + e.Message; }
                list[i] = p;
            }
            _probes = list;
            ProbeStartedUtc = DateTime.UtcNow.ToString("o");
        }

        internal static void StopProbe()
        {
            var list = _probes;
            _probes = null;
            if (list == null) return;
            for (int i = 0; i < list.Length; i++) { try { if (list[i].Started) list[i].Rec.Dispose(); } catch { } }
        }

        internal static Dictionary<string, object> Inventory()
        {
            var rows = new List<KeyValuePair<string, H.Reading>>();
            var o = new Dictionary<string, object>();
            string Try(Func<string> f) { try { return f(); } catch (Exception e) { return "unavailable: " + e.GetType().Name; } }
            o["unityVersion"] = Try(() => Application.unityVersion);
            o["gameVersion"] = Try(() => RimWorld.VersionControl.CurrentVersionStringWithRev);
            o["harmonyVersion"] = Try(() => typeof(Harmony).Assembly.GetName().Version.ToString());
            o["gcMode"] = Try(() => GarbageCollector.GCMode.ToString());
            o["gcIncremental"] = Try(() => GarbageCollector.isIncremental ? "true" : "false");
            o["gcTiming"] = "GC pause time: unsupported (no validated timing source in this player); spike.gc-timing records coincidence only";
            o["presentationFps"] = "unsupported: Root.Update cadence is not displayed FPS (tps.presentation-fps)";
            var cap = JawaBenchHealth.ReadCap();
            o["verseLog"] = new { state = cap.Word, text = cap.Text, headroom = cap.Headroom.Render(), capResets = JawaBenchHealth.CapResets.Resets };

            foreach (var id in H.MetricIds)
                if (id != H.MCapInv && id != H.MProfiler) rows.Add(new KeyValuePair<string, H.Reading>(id, JawaBenchHealth.SourceReading(id)));
            rows.Add(new KeyValuePair<string, H.Reading>(H.MProfiler, !JawaBenchHealth.Sw.On(H.MProfiler) ? H.Reading.SwitchedOff()
                : JawaBenchHealthProfiler.Running ? H.Reading.Ok(JawaBenchHealthProfiler.Keys.Length, "methods timed")
                : H.Reading.Unavailable("not running (" + JawaBenchHealthProfiler.Status + ")")));

            var list = _probes;
            if (list == null)
                rows.Add(new KeyValuePair<string, H.Reading>("unity.recorders", H.Reading.Unavailable("not probed: jawa/health action=probe, then status a few frames later")));
            else
                foreach (var p in list)
                {
                    H.Reading r;
                    try { r = H.ClassifyRecorder(p.Started, p.Error, p.Started && p.Rec.Valid, p.Started && p.Rec.Valid ? p.Rec.Count : 0,
                                                  p.Started && p.Rec.Valid ? p.Rec.LastValue : 0, p.Unit); }
                    catch (Exception e) { r = H.Reading.Failed(e.GetType().Name + ": " + e.Message); }
                    rows.Add(new KeyValuePair<string, H.Reading>("unity." + p.Category + "/" + p.Name, r));
                }
            o["sources"] = rows.ToDictionary(kv => kv.Key, kv => (object)new { status = kv.Value.Word, value = kv.Value.IsOk ? (object)kv.Value.Value : null, unit = kv.Value.IsOk ? kv.Value.Unit : null, reason = kv.Value.Reason });
            o["summary"] = H.InventorySummary(rows);
            o["probeStartedUtc"] = ProbeStartedUtc;
            return o;
        }
    }
}
