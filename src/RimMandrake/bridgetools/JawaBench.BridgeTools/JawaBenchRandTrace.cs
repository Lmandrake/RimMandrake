// JawaBenchRandTrace.cs - a counter on every Verse.Rand draw, with its caller and its phase, for the first ticks of a scene run.
//
// Item RIMMANDRAKE_FIND_RAND_DRAWS_PARTING_RUNS_EVEN_STEP. Runs from one fixture save and one written-back random state part
// on Rand.iterations by tick 1 to 22 (design/specs/2026-11-23-bridge-v2/experiments/play_vs_step_rand_draws.md). This tracer
// names the draws that differ: a postfix on the two getters that move the stream (Rand.Value and Rand.Int; every other draw
// helper calls one of them) counts each draw by (tick, phase, caller).
//
// The window opens at the scene run's random write-back (JawaBenchSceneTick.WriteRand calls Begin) and closes after
// `window` ticks. Phases: "pre" = after the write and before the first tick; "tick" = inside DoSingleTick (Enter/Exit from
// JawaBenchVitals.TickPre/TickPost, the ONE hook on that method); "frame" = between ticks. A draw at a pushed state
// (Rand.PushState, the *Seeded helpers) is counted apart ("pushed"): it does not move the global stream.
//
// THE INSTRUMENT PROVES IT CAN SEE: each traced tick keeps the stream's iterations at Enter and at Exit. When the hooked
// depth-0 draws of the tick equal that delta, the tick is `seen`. A draw that the JIT inlined into its caller would
// move the stream without the postfix: such a tick reads seen=false, and the verdict (rand_trace_verdict.py) refuses it.
// A Seed write at depth 0 inside a tick also breaks the equality; it is counted as `reseeds` so the two stay apart.
//
// ISOLATE (the fix experiment): `isolate=<Type:Method>,...` wraps each named method in Rand.PushState / PopState while the tracer is
// armed, so the draws inside it leave the global stream still (the Multiplayer mod's method). Its first use: the fish flecks of
// Verse.FishShadowComponent:MapComponentTick, which fire on a tick set by an object identity hash (new at every load). The patch
// stays on the method after `off`, inert: its prefix pushes only while the method is in the armed set.
//
// The postfix draws nothing (reading StateCompressed and the stack count draws nothing). Main thread only: a draw from
// another thread is counted as `foreign` and not traced. No jawa/ prefix in prose other than the one tool name.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using HarmonyLib;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchRandTrace
    {
        internal const string HarmonyId = "mandrake.jawabench.randtrace";
        internal static string HookStatus = "not installed", HookDetail;
        private static bool _installed;

        // state: off -> waiting (armed, no write-back yet) -> tracing -> done
        internal static string State = "off";
        internal static int Window = 40, Depth = 3;
        internal static int AnchorTick = -1;           // TicksGame at the write-back
        internal static ulong AnchorState;
        internal static bool InTick;
        private static int _curTick;                   // the tick being run (TicksGame + 1 at Enter) or, between ticks, TicksGame
        private static uint _iterEnter;
        private static int _hookedInTick, _reseedsInTick;
        internal static long Foreign, Faults, Draws, Pushed;
        internal static string LastFault;

        private static Func<ulong> _state;
        private static Func<int> _depth;

        internal sealed class TickRow { public int t; public long i0, i1; public int hooked, reseeds; public bool seen; }
        internal static readonly Dictionary<string, int> Counts = new Dictionary<string, int>(StringComparer.Ordinal);
        internal static readonly List<TickRow> Ticks = new List<TickRow>();
        private static readonly Dictionary<MethodBase, string> _names = new Dictionary<MethodBase, string>();
        private static readonly HashSet<MethodBase> _isoPatched = new HashSet<MethodBase>();
        internal static readonly HashSet<MethodBase> IsoActive = new HashSet<MethodBase>();
        internal static readonly List<string> IsoNames = new List<string>();
        internal static long IsoCalls;

        private static bool Tracing => State == "tracing";

        internal static string Install()
        {
            if (_installed) return HookStatus == "installed" ? null : HookStatus + ": " + HookDetail;
            _installed = true;
            try
            {
                var g = AccessTools.PropertyGetter(typeof(Rand), "StateCompressed");
                var stack = AccessTools.Field(typeof(Rand), "stateStack");
                if (g == null || stack == null) { HookStatus = "failed"; HookDetail = "Rand.StateCompressed or Rand.stateStack did not resolve"; return HookDetail; }
                _state = (Func<ulong>)Delegate.CreateDelegate(typeof(Func<ulong>), g);
                var st = (Stack<ulong>)stack.GetValue(null);
                _depth = () => st.Count;
                var h = new Harmony(HarmonyId);
                var post = new HarmonyMethod(typeof(JawaBenchRandTrace).GetMethod(nameof(DrawPost), BindingFlags.Static | BindingFlags.NonPublic));
                var seedPost = new HarmonyMethod(typeof(JawaBenchRandTrace).GetMethod(nameof(SeedPost), BindingFlags.Static | BindingFlags.NonPublic));
                h.Patch(AccessTools.PropertyGetter(typeof(Rand), nameof(Rand.Value)), postfix: post);
                h.Patch(AccessTools.PropertyGetter(typeof(Rand), nameof(Rand.Int)), postfix: post);
                h.Patch(AccessTools.PropertySetter(typeof(Rand), nameof(Rand.Seed)), postfix: seedPost);
                HookStatus = "installed";
                return null;
            }
            catch (Exception e) { HookStatus = "failed"; HookDetail = e.GetType().Name + ": " + e.Message; return HookDetail; }
        }

        internal static void Arm(int window, int depth)
        {
            Window = Math.Max(1, window); Depth = Math.Max(1, Math.Min(depth, 8));
            Counts.Clear(); Ticks.Clear(); Foreign = Faults = Draws = Pushed = 0; LastFault = null;
            AnchorTick = -1; InTick = false;
            State = "waiting";
        }

        internal static void Off() { State = "off"; InTick = false; IsoActive.Clear(); IsoNames.Clear(); }

        /// <summary>Resolve and patch each `Type:Method` of the list (once per method), and make the list the armed set. Null, or why not.</summary>
        internal static string Isolate(string list)
        {
            IsoActive.Clear(); IsoNames.Clear(); IsoCalls = 0;
            if (string.IsNullOrWhiteSpace(list)) return null;
            var h = new Harmony(HarmonyId);
            foreach (var raw in list.Split(','))
            {
                string name = raw.Trim();
                if (name.Length == 0) continue;
                MethodBase m;
                try { m = AccessTools.Method(name); } catch (Exception e) { return name + ": " + e.Message; }
                if (m == null) return name + ": no such method (give Namespace.Type:Method)";
                if (!_isoPatched.Contains(m))
                {
                    try
                    {
                        h.Patch(m, prefix: new HarmonyMethod(typeof(JawaBenchRandTrace).GetMethod(nameof(IsoPre), BindingFlags.Static | BindingFlags.NonPublic)),
                                finalizer: new HarmonyMethod(typeof(JawaBenchRandTrace).GetMethod(nameof(IsoFin), BindingFlags.Static | BindingFlags.NonPublic)));
                    }
                    catch (Exception e) { return name + ": the patch failed: " + e.GetType().Name + ": " + e.Message; }
                    _isoPatched.Add(m);
                }
                IsoActive.Add(m); IsoNames.Add(name);
            }
            return null;
        }

        private static void IsoPre(MethodBase __originalMethod, out bool __state)
        {
            __state = false;
            try
            {
                if (State == "off" || !UnityData.IsInMainThread || !IsoActive.Contains(__originalMethod)) return;
                Rand.PushState();
                __state = true;
                IsoCalls++;
            }
            catch (Exception e) { Faults++; LastFault = "isolate push: " + e.Message; }
        }

        /// <summary>A void finalizer: a throw of the method goes on unchanged; an orphan (no push) pops nothing.</summary>
        private static void IsoFin(bool __state)
        {
            if (__state)
            {
                try { Rand.PopState(); }
                catch (Exception e) { Faults++; LastFault = "isolate pop: " + e.Message; }
            }
        }

        /// <summary>From JawaBenchSceneTick.WriteRand, after the write held. Main thread.</summary>
        internal static void Begin(ulong written)
        {
            if (State != "waiting") return;              // one window per arm: a second write-back does not reopen it
            try
            {
                Counts.Clear(); Ticks.Clear(); Draws = Pushed = 0;
                AnchorTick = Find.TickManager.TicksGame; AnchorState = written; _curTick = AnchorTick;
                State = "tracing";
            }
            catch (Exception e) { Faults++; LastFault = "begin: " + e.Message; }
        }

        /// <summary>From JawaBenchVitals.TickPre, before its own gate. Draws nothing.</summary>
        internal static void Enter(TickManager tm)
        {
            if (!Tracing) return;
            try
            {
                _curTick = tm.TicksGame + 1;
                if (_curTick > AnchorTick + Window) { State = "done"; InTick = false; return; }
                InTick = true; _hookedInTick = 0; _reseedsInTick = 0;
                _iterEnter = (uint)(_state() >> 32);
            }
            catch (Exception e) { Faults++; LastFault = "enter: " + e.Message; }
        }

        /// <summary>From JawaBenchVitals.TickPost and TickFin. Draws nothing.</summary>
        internal static void Exit()
        {
            if (!Tracing || !InTick) return;
            try
            {
                InTick = false;
                uint i1 = (uint)(_state() >> 32);
                Ticks.Add(new TickRow { t = _curTick, i0 = _iterEnter, i1 = i1, hooked = _hookedInTick, reseeds = _reseedsInTick,
                                        seen = _reseedsInTick == 0 && unchecked(i1 - _iterEnter) == (uint)_hookedInTick });
            }
            catch (Exception e) { Faults++; LastFault = "exit: " + e.Message; }
        }

        private static void SeedPost(bool __runOriginal)
        {
            if (!__runOriginal || !Tracing || !InTick) return;
            try { if (_depth() == 0) _reseedsInTick++; } catch { Faults++; }
        }

        private static void DrawPost(bool __runOriginal)
        {
            if (!__runOriginal || !Tracing) return;
            try
            {
                if (!UnityData.IsInMainThread) { Interlocked.Increment(ref Foreign); return; }
                bool pushed = _depth() > 0;
                if (pushed) Pushed++; else { Draws++; if (InTick) _hookedInTick++; }
                string phase = InTick ? "tick" : (Ticks.Count == 0 ? "pre" : "frame");
                string key = _curTick + "|" + phase + (pushed ? "+pushed" : "") + "|" + Caller();
                Counts.TryGetValue(key, out int n);
                Counts[key] = n + 1;
            }
            catch (Exception e) { Faults++; LastFault = "draw: " + e.GetType().Name + ": " + e.Message; }
        }

        /// <summary>The first `Depth` frames above the draw that are not Rand, Harmony or this class, joined by " < ".</summary>
        private static string Caller()
        {
            var frames = new StackTrace(2, false).GetFrames();
            if (frames == null) return "?";
            var names = new List<string>(Depth);
            foreach (var f in frames)
            {
                var m = f.GetMethod();
                if (m == null) continue;
                var dt = m.DeclaringType;
                if (dt == typeof(Rand) || dt == typeof(JawaBenchRandTrace)) continue;
                if (m.Name.StartsWith("Verse.Rand.", StringComparison.Ordinal) || (dt == null && m.Name.IndexOf("Rand", StringComparison.Ordinal) >= 0)) continue;    // the patched getter's replacement (MonoMod names it Verse.Rand.get_Value_Patch1)
                if (dt != null && dt.Namespace != null && dt.Namespace.StartsWith("HarmonyLib", StringComparison.Ordinal)) continue;
                if (!_names.TryGetValue(m, out string s)) { s = (dt != null ? dt.FullName : "?") + "." + m.Name; _names[m] = s; }
                names.Add(s);
                if (names.Count >= Depth) break;
            }
            return names.Count == 0 ? "?" : string.Join(" < ", names);
        }

        internal static object Read(int maxRows)
        {
            var rows = Counts.Select(kv => { var p = kv.Key.Split(new[] { '|' }, 3); return new { t = int.Parse(p[0]), ph = p[1], c = p[2], n = kv.Value }; })
                             .OrderBy(r => r.t).ThenBy(r => r.ph, StringComparer.Ordinal).ThenBy(r => r.c, StringComparer.Ordinal).ToList();
            bool cut = rows.Count > maxRows;
            return new
            {
                success = true, state = State, hook = HookStatus, hookDetail = HookDetail, window = Window, anchorTick = AnchorTick,
                anchorState = AnchorState.ToString(), isolate = IsoNames.ToList(), isoCalls = IsoCalls, draws = Draws, pushed = Pushed, foreign = Foreign, faults = Faults, lastFault = LastFault,
                ticks = Ticks.Select(x => new { x.t, x.i0, x.i1, x.hooked, x.reseeds, x.seen }).ToList(),
                ticksSeen = Ticks.Count(x => x.seen), ticksTraced = Ticks.Count,
                rows = cut ? rows.Take(maxRows).ToList() : rows, rowCount = rows.Count, rowsCut = cut
            };
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/rand_trace",
            Description =
                "READ ONLY for the game (its postfix draws nothing): count every Verse.Rand draw by tick, phase and caller for the " +
                "first ticks of the next scene run that writes back a random state. action=arm window=<ticks> depth=<frames>: install " +
                "the postfix on Rand.Value and Rand.Int (once) and wait for the write-back. action=read: the counts so far. " +
                "isolate=<Namespace.Type:Method,...> (arm): wrap each in Rand.PushState/PopState while armed, so its draws leave the global stream still. " +
                "action=off: stop counting and isolating. Phases: pre (after the write-back, before the first tick), tick (inside DoSingleTick), " +
                "frame (between ticks); +pushed = a draw at a pushed state that leaves the global stream still. Each traced tick reads " +
                "seen=true only when its hooked draws equal the stream's iterations delta: a draw the hook could not see reads false.",
            ResultDescription =
                "success, state (off|waiting|tracing|done), hook, window, anchorTick, anchorState, draws, pushed, foreign, faults, " +
                "ticks[] {t, i0, i1, hooked, reseeds, seen}, ticksSeen, ticksTraced, rows[] {t, ph, c, n}, rowCount, rowsCut.")]
        public static async Task<object> RandTrace(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'arm', 'read' (default) or 'off'.")] string action = "read",
            [ToolParameter(Description = "arm: ticks to trace after the write-back, 1 to 600.")] int window = 40,
            [ToolParameter(Description = "arm: caller frames kept per draw, 1 to 8.")] int depth = 3,
            [ToolParameter(Description = "read: the most rows returned.")] int maxRows = 20000,
            [ToolParameter(Description = "arm: methods whose draws are held off the global stream, 'Namespace.Type:Method' comma-separated; empty: none.")] string isolate = "")
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string a = (action ?? "read").Trim().ToLowerInvariant();
                if (a == "arm")
                {
                    if (window < 1 || window > 600) return new { success = false, message = "BAD_ARGS: window is 1 to 600 ticks" };
                    string why = JawaBenchRandTrace.Install();
                    if (why != null) return new { success = false, message = "COULD_NOT_LOOK: the Rand postfix did not install: " + why };
                    JawaBenchRandTrace.Arm(window, depth);
                    string iso = JawaBenchRandTrace.Isolate(isolate);
                    if (iso != null) { JawaBenchRandTrace.Off(); return new { success = false, message = "BAD_ARGS: isolate: " + iso }; }
                    return new { success = true, state = JawaBenchRandTrace.State, window = JawaBenchRandTrace.Window, depth = JawaBenchRandTrace.Depth, isolate = JawaBenchRandTrace.IsoNames.ToList() };
                }
                if (a == "off") { JawaBenchRandTrace.Off(); return new { success = true, state = JawaBenchRandTrace.State }; }
                if (a == "read") return JawaBenchRandTrace.Read(Math.Max(1, maxRows));
                return new { success = false, message = "BAD_ACTION: action must be 'arm', 'read' or 'off'" };
            }).ConfigureAwait(false);
        }
    }
}
