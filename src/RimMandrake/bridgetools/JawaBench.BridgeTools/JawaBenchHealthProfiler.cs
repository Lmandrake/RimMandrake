// JawaBenchHealthProfiler.cs - opt.profiler (game_health_record.md), with opt.own-counters MERGED into it as the
// preset "own": an ON-DEMAND, EXPIRING timer on an EXACT allowlist of named methods.
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
                    // marked patched only once Patch returned (c02.F6): a Patch that throws must not leave the method
                    // recorded as hooked, or every later start skips it and its meter reads a silent zero
                    foreach (var mb in map.Keys)
                        if (!_patched.Contains(mb)) { _harmony.Patch(mb, prefix: pre, finalizer: fin); _patched.Add(mb); }
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
}
