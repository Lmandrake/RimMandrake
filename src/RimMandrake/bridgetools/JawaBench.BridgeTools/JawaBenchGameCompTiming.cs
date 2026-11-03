// JawaBenchGameCompTiming.cs - per-GameComponent tick timing and one-off stall capture (GAMECOMP_STALL_HUNT_SEVEN_SECONDS).
//
// The twin of jawa/map_comp_timing for GameComponentUtility.GameComponentTick, the TPS record's `gameComp` stage. The
// stalls it hunts are ONE-OFF (6.76 s at tg 7501, 2.88 s 18 ticks after a load, Rot save on the 550 list), so beside
// per-type totals it keeps every single call over `spikeMs` with its game tick and ticks since the last load seen, and
// names the component that took the most of the WORST stage call (stageMaxTop*), so a stall is attributed as one event.
//
// Unlike a MapComponent, the patch set does not depend on what is spawned: every non-abstract GameComponent subclass
// in every loaded assembly (GenTypes) is patched, so the timers stay valid when the save is reloaded while armed -
// the only way to see the post-load stall. Modes:
//   run    (default) arm, wait for N real ticks at the CALLER's speed (never changes speed), report, disarm.
//   arm    install and return at once; timing stays live until `maxSeconds` from now, then the timers go INERT
//          (a prefix that returns at once) until `read`/`disarm`/another arm removes them.
//   read   report what has been caught so far, stay armed.
//   disarm remove every timer, then report.
// Every arm starts a new SESSION; a run only reports and cleans up its own session, so a later arm is never torn
// down by an older run finishing.
// Same Harmony discipline as JawaBenchMapCompTiming.cs: no Harmony type in a static initializer, every HarmonyLib call
// in a try/catch, UnpatchAll(own id) whenever a run ends or fails. Hook state: `__state` 0 means "do nothing" (the
// default when our prefix never ran because an earlier prefix threw), and every finalizer zeroes it by ref before
// acting, so a finalizer Harmony runs twice is a no-op the second time. Only the outermost timed call on the main
// thread is counted. Elapsed time counts CPU, GC pauses its allocations trigger, and blocking: a lead, not a verdict.
// Bookkeeping (rows, spikes, loads, stage attribution, owner roll-up) is the pure JawaBenchCompTimingCore, unit-tested.

#if JAWA_GM_TOOLS
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
    internal static class JawaBenchGameCompTimer
    {
        internal const string HarmonyId = "mandrake.jawabench.gamecomptiming";
        internal const long Nested = -2;        // __state: depth taken, not timed (0 = nothing, > 0 = start stamp)
        internal static JawaBenchCompTimingCore<Type> Core;
        internal static volatile bool Armed;
        internal static int Session;            // bumped by every Install; a run owns only its own
        internal static bool Installed;
        internal static string UninstallError;  // set when UnpatchAll threw; Installed stays true and Install refuses
        internal static long DeadlineStamp;     // Stopwatch timestamp after which the timers are inert
        internal static int MainThreadId = -1;
        internal static int Depth;
        internal static int StageDepth;         // a component re-entering the stage is nested, not a second stage call
        internal static long Foreign;           // Interlocked: worker threads write it
        internal static long StageCalls, StageTotal;
        internal static long ArmedAtStamp;
        internal static int ArmedAtTick = -1;
        internal static int PatchedMethods;
        internal static readonly List<string> PatchFailures = new List<string>();

        static bool Running() => Armed && Core != null && Stopwatch.GetTimestamp() < DeadlineStamp;
        static bool OnMain() => Thread.CurrentThread.ManagedThreadId == MainThreadId;
        static int Tick() => Current.Game?.tickManager?.TicksGame ?? -1;   // null at the menu / mid-load

        // The stage: GameComponentUtility.GameComponentTick, once per game tick. It also tells the core a tick began
        // (and which Game object is running, so a reload while armed is seen as a load).
        internal static void StagePre(out long __state)
        {
            __state = 0;
            if (!Running() || !OnMain()) return;
            if (++StageDepth > 1) { __state = Nested; return; }
            Core.NoteTick(Current.Game, Tick());
            Core.StageBegin();
            __state = Stopwatch.GetTimestamp();
        }

        internal static void StageFin(ref long __state)
        {
            long s = __state; __state = 0;
            if (s == 0) return;
            if (StageDepth > 0) StageDepth--;
            if (s < 0 || Core == null) return;
            long d = Stopwatch.GetTimestamp() - s;
            StageCalls++; StageTotal += d;
            Core.StageEnd(d, Tick());
        }

        internal static void Pre(out long __state)
        {
            __state = 0;
            if (!Running()) return;
            if (!OnMain()) { Interlocked.Increment(ref Foreign); return; }
            Depth++;
            __state = Depth == 1 ? Stopwatch.GetTimestamp() : Nested;
        }

        internal static void Fin(GameComponent __instance, ref long __state)
        {
            long s = __state; __state = 0;
            if (s == 0) return;
            if (Depth > 0) Depth--;
            if (s < 0 || __instance == null || Core == null) return;
            Core.Add(__instance.GetType(), Stopwatch.GetTimestamp() - s, Tick());
        }

        /// <summary>Main thread. Removes our timers; null on success (or when none are installed), else the error.
        /// A failed UnpatchAll leaves Installed true so a later call retries and Install refuses.</summary>
        internal static string Uninstall()
        {
            Armed = false;
            if (!Installed) return null;
            try { new Harmony(HarmonyId).UnpatchAll(HarmonyId); }
            catch (Exception ex) { return UninstallError = "UnpatchAll failed: " + ex.GetType().Name + " " + ex.Message; }
            Installed = false; UninstallError = null; Depth = 0; StageDepth = 0;
            return null;
        }

        /// <summary>Main thread. (Re)installs timers on the stage and every GameComponentTick override; returns the
        /// new session token, or 0 with <paramref name="err"/> set.</summary>
        internal static int Install(double spikeMs, int spikeCap, int maxSeconds, out string err)
        {
            err = Uninstall();
            if (err != null) { err = "previous timers could not be removed: " + err; return 0; }
            int token = ++Session;
            double toTicks = Stopwatch.Frequency / 1000.0;
            Core = new JawaBenchCompTimingCore<Type>((long)Math.Round(Math.Max(0, spikeMs) * toTicks), spikeCap);
            Core.Arm(Current.Game);
            Depth = 0; StageDepth = 0; Interlocked.Exchange(ref Foreign, 0); StageCalls = 0; StageTotal = 0;
            PatchedMethods = 0; PatchFailures.Clear();
            MainThreadId = Thread.CurrentThread.ManagedThreadId;
            var methods = new HashSet<MethodInfo>();
            foreach (Type t in GenTypes.AllSubclassesNonAbstract(typeof(GameComponent)))
            {
                try
                {
                    if (t.ContainsGenericParameters) continue;
                    MethodInfo m = t.GetMethod("GameComponentTick", BindingFlags.Public | BindingFlags.Instance, null, Type.EmptyTypes, null);
                    if (m == null || m.DeclaringType == typeof(GameComponent) || m.IsAbstract) continue;
                    // One MethodInfo per declaring type: a base override inherited by several subclasses is patched once.
                    m = m.DeclaringType.GetMethod("GameComponentTick", BindingFlags.Public | BindingFlags.Instance | BindingFlags.DeclaredOnly, null, Type.EmptyTypes, null) ?? m;
                    methods.Add(m);
                }
                catch (Exception ex) { PatchFailures.Add(t.FullName + ": " + ex.GetType().Name + " " + ex.Message); }
            }
            try
            {
                var h = new Harmony(HarmonyId);
                Installed = true;
                var self = typeof(JawaBenchGameCompTimer);
                const BindingFlags F = BindingFlags.Static | BindingFlags.NonPublic;
                MethodInfo stage = AccessTools.Method(typeof(GameComponentUtility), nameof(GameComponentUtility.GameComponentTick));
                if (stage == null) { Uninstall(); err = "GameComponentUtility.GameComponentTick not found"; return 0; }
                h.Patch(stage, prefix: new HarmonyMethod(self.GetMethod("StagePre", F)), finalizer: new HarmonyMethod(self.GetMethod("StageFin", F)));
                var pre = new HarmonyMethod(self.GetMethod("Pre", F));
                var fin = new HarmonyMethod(self.GetMethod("Fin", F));
                foreach (var m in methods)
                {
                    try { h.Patch(m, prefix: pre, finalizer: fin); PatchedMethods++; }
                    catch (Exception ex) { PatchFailures.Add(m.DeclaringType?.FullName + ": " + ex.GetType().Name + " " + ex.Message); }
                }
            }
            catch (Exception ex) { Uninstall(); err = "Harmony unavailable: " + ex.Message; return 0; }
            ArmedAtStamp = Stopwatch.GetTimestamp();
            ArmedAtTick = Tick();
            DeadlineStamp = ArmedAtStamp + (long)Math.Max(1, Math.Min(3600, maxSeconds)) * Stopwatch.Frequency;
            Armed = true;
            return token;
        }

        /// <summary>Main thread. The reply; never mutates timing state.</summary>
        internal static object Report(int top, string mode)
        {
            var core = Core;
            if (core == null) return new { success = false, message = "Nothing armed: call mode=arm or mode=run first." };
            double f = 1000.0 / Stopwatch.Frequency;
            int perTick = Math.Max(1, core.TicksObserved);
            var asmToPkg = new Dictionary<Assembly, string>();
            foreach (var mod in LoadedModManager.RunningModsListForReading)
            {
                if (mod.assemblies?.loadedAssemblies == null) continue;
                foreach (var a in mod.assemblies.loadedAssemblies) if (!asmToPkg.ContainsKey(a)) asmToPkg[a] = mod.PackageId;
            }
            string Owner(Type t) => t == null ? "?" : asmToPkg.TryGetValue(t.Assembly, out var p) ? p
                : (t.Assembly == typeof(GameComponent).Assembly ? "ludeon (Assembly-CSharp)" : "?");
            int n = Math.Max(1, top);
            var rows = core.Ranked().Take(n).Select(kv => new
            {
                type = kv.Key.FullName,
                assembly = kv.Key.Assembly.GetName().Name,
                packageId = Owner(kv.Key),
                calls = kv.Value.Calls,
                totalMs = Math.Round(kv.Value.Total * f, 2),
                msPerTick = Math.Round(kv.Value.Total * f / perTick, 3),
                maxMs = Math.Round(kv.Value.Max * f, 2),
                maxAtTick = kv.Value.MaxAtTick,
            }).ToList();
            var spikes = core.RankedSpikes().Select(s => new
            {
                type = s.Key.FullName,
                packageId = Owner(s.Key),
                ms = Math.Round(s.Dur * f, 2),
                tick = s.Tick,
                ticksSinceLoad = s.SinceLoad,
                load = s.Load,
            }).ToList();
            var byMod = core.ByOwner(Owner).Take(n).Select(o => new
            {
                packageId = o.Owner,
                components = o.Keys,
                calls = o.Calls,
                totalMs = Math.Round(o.Total * f, 2),
                msPerTick = Math.Round(o.Total * f / perTick, 3),
                maxMs = Math.Round(o.Max * f, 2),
            }).ToList();
            double sum = core.Rows.Values.Sum(r => r.Total) * f;
            double stage = StageTotal * f;
            long now = Stopwatch.GetTimestamp();
            bool topKnown = core.StageMaxTopDur >= 0 && core.StageMaxTop != null;
            return new
            {
                success = true,
                mode,
                session = Session,
                armed = Armed && Installed,
                live = Armed && Installed && now < DeadlineStamp,
                uninstallError = UninstallError,
                secondsArmed = Math.Round((now - ArmedAtStamp) / (double)Stopwatch.Frequency, 1),
                secondsLeft = Math.Round(Math.Max(0, DeadlineStamp - now) / (double)Stopwatch.Frequency, 1),
                armedAtTick = ArmedAtTick,
                ticksObserved = core.TicksObserved,
                loadsSeen = core.Loads,
                patchedMethods = PatchedMethods,
                patchFailures = PatchFailures.ToList(),
                foreignThreadCalls = Interlocked.Read(ref Foreign),
                stageCalls = StageCalls,
                stageMs = Math.Round(stage, 1),
                stageMaxMs = Math.Round(core.StageMax * f, 2),
                stageMaxAtTick = core.StageMaxAtTick,
                stageMaxLoad = core.StageMaxLoad,
                stageMaxSinceLoad = core.StageMaxSinceLoad,
                // The component that took the most of the worst stage call - the same event, not a look-alike number.
                stageMaxTopType = topKnown ? core.StageMaxTop.FullName : null,
                stageMaxTopPackageId = topKnown ? Owner(core.StageMaxTop) : null,
                stageMaxTopMs = topKnown ? Math.Round(core.StageMaxTopDur * f, 2) : (double?)null,
                componentSumMs = Math.Round(sum, 1),
                // < 1: part of the stage ran outside any patched override (base-class work, a non-overriding comp,
                // a patch that failed) - read patchFailures before trusting the ranking.
                coverage = stage > 0 ? Math.Round(sum / stage, 3) : (double?)null,
                spikeMs = Math.Round(core.SpikeThreshold * f, 1),
                spikesSeen = core.SpikesSeen,
                spikes,
                componentsTimed = core.Rows.Count,
                components = rows,
                byMod,
            };
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/game_comp_timing",
            Description =
                "TEST/DIAGNOSTIC. Times every GameComponent's GameComponentTick (the TPS record's gameComp stage) and " +
                "catches one-off stalls: every single call >= spikeMs is kept with its game tick and ticks since the last " +
                "load seen, and the worst stage call names the component that took most of it. Patches every " +
                "GameComponent subclass, so it stays valid across a save reload. mode=run (default): arm, wait for N real " +
                "ticks at the CALLER's speed (never changes speed), report, disarm. mode=arm: install and return; live for " +
                "maxSeconds, then inert until read/disarm. mode=read: report, stay armed. mode=disarm: remove, report. " +
                "Ranked by component and by owning mod (packageId of the mod whose assemblies hold the type). Elapsed time " +
                "(CPU, GC, blocking): a lead, not a verdict.",
            ResultDescription =
                "success, mode, session, armed, live, uninstallError, secondsArmed, secondsLeft, armedAtTick, ticksObserved, " +
                "loadsSeen, patchedMethods, patchFailures[], foreignThreadCalls, stageCalls, stageMs, stageMaxMs, " +
                "stageMaxAtTick, stageMaxLoad, stageMaxSinceLoad, stageMaxTopType, stageMaxTopPackageId, stageMaxTopMs, " +
                "componentSumMs, coverage, spikeMs, spikesSeen, spikes[] of {type, packageId, ms, tick, ticksSinceLoad, load}, " +
                "componentsTimed, components[] of {type, assembly, packageId, calls, totalMs, msPerTick, maxMs, maxAtTick}, " +
                "byMod[] of {packageId, components, calls, totalMs, msPerTick, maxMs}.")]
        public static async Task<object> GameCompTiming(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "run (default) | arm | read | disarm.")] string mode = "run",
            [ToolParameter(Description = "mode=run: real game ticks to sample (default 300).")] int ticks = 300,
            [ToolParameter(Description = "run: give up after this many real seconds; arm: stay live this long (default 120, max 3600).")] int maxSeconds = 120,
            [ToolParameter(Description = "A single call at or above this many ms is a spike (default 100; 0 records none).")] double spikeMs = 100,
            [ToolParameter(Description = "How many spikes to keep, largest first (default 50).")] int spikeCap = 50,
            [ToolParameter(Description = "How many components and mods to return, largest first (default 30).")] int top = 30,
            [ToolParameter(Description = "read/disarm: act only if this is still the current session (the `session` an arm returned); 0 = any.")] int session = 0)
        {
            mode = (mode ?? "run").Trim().ToLowerInvariant();
            maxSeconds = Math.Max(1, Math.Min(3600, maxSeconds));
            spikeCap = Math.Max(0, Math.Min(1000, spikeCap));
            if (mode == "read")
                return await ctx.MainThread.InvokeAsync(() => session > 0 && JawaBenchGameCompTimer.Session != session
                    ? Fail("session " + session + " is gone: the current session is " + JawaBenchGameCompTimer.Session + ".")
                    : JawaBenchGameCompTimer.Report(top, mode));
            if (mode == "disarm")
                return await ctx.MainThread.InvokeAsync(() =>
                {
                    if (session > 0 && JawaBenchGameCompTimer.Session != session)
                        return Fail("session " + session + " is gone: the current session is " + JawaBenchGameCompTimer.Session + "; its timers are left to it.");
                    string err = JawaBenchGameCompTimer.Uninstall();   // first, so the reply reads armed=false
                    return err != null ? Fail(err) : JawaBenchGameCompTimer.Report(top, mode);
                });
            if (mode != "arm" && mode != "run") return Fail("mode must be run, arm, read or disarm (got '" + mode + "').");

            int token = 0;
            bool keep = false;
            try
            {
                string err = null;
                token = await ctx.MainThread.InvokeAsync(() => JawaBenchGameCompTimer.Install(spikeMs, spikeCap, maxSeconds, out err));
                if (token == 0) return Fail(err ?? "install failed");
                if (mode == "arm")
                {
                    object armed = await ctx.MainThread.InvokeAsync(() => JawaBenchGameCompTimer.Session == token
                        ? JawaBenchGameCompTimer.Report(top, mode)
                        : Fail("superseded: another arm started session " + JawaBenchGameCompTimer.Session + " before this one reported."));
                    keep = true;   // only now: a failed report above leaves the finally to remove this session's timers
                    return armed;
                }
                if (ticks < 1) ticks = 1;
                var sw = Stopwatch.StartNew();
                var core = JawaBenchGameCompTimer.Core;
                // Read off the main thread on purpose: a load in progress must not block the wait, and an int read is
                // atomic. A newer arm (another session) ends this wait at once.
                while (Volatile.Read(ref core.TicksObserved) < ticks && sw.Elapsed.TotalSeconds < maxSeconds
                       && Volatile.Read(ref JawaBenchGameCompTimer.Session) == token)
                    await Task.Delay(250, cancellationToken).ConfigureAwait(false);
                return await ctx.MainThread.InvokeAsync(() =>
                {
                    if (JawaBenchGameCompTimer.Session != token)
                        return Fail("superseded: another arm started session " + JawaBenchGameCompTimer.Session + " while this run waited; its timers are left to it.");
                    // Remove first, so a failed UnpatchAll is the reply rather than a success that hides it.
                    string uerr = JawaBenchGameCompTimer.Uninstall();
                    return uerr != null ? Fail(uerr) : JawaBenchGameCompTimer.Report(top, mode);
                });
            }
            finally
            {
                if (!keep && token != 0)
                {
                    try
                    {
                        await ctx.MainThread.InvokeAsync(() =>
                        {
                            if (JawaBenchGameCompTimer.Session == token) JawaBenchGameCompTimer.Uninstall();
                            return 0;
                        });
                    }
                    catch { }
                }
            }
        }
    }
}
#endif
