// JawaBenchMapCompTiming.cs - one-off, per-MapComponent tick timing (FULL_LIST_TPS_DIAGNOSE_EIGHT_NOT_SIXTY,
// ROT_MAPCOMP_HUNT_FORTY_SEVEN_MS).
//
// The always-on TPS record times MapComponentUtility.MapComponentTick as ONE stage (per-component timing is
// ruled out of the always-on path). When that stage dominates, this tool names the component: it patches every
// distinct MapComponentTick override on the current map with a prefix + finalizer timer, lets the game run the
// requested number of REAL ticks at whatever speed the caller set, then unpatches everything and returns
// per-type totals with the owning mod. It never changes speed and never ticks anything itself.
//
// Harmony contact point #3: same discipline as JawaBenchArgGuard.cs - no Harmony type in a static initializer,
// every HarmonyLib call inside a try/catch, and UnpatchAll(own id) in a finally so a cancelled or failed call
// cannot leave timers installed. Only the outermost timed call on the main thread is counted (an override that
// calls base.MapComponentTick of another patched override is not double counted).
//
// Elapsed time inside a component's tick: CPU, GC suspensions triggered by its allocations and blocking all
// count. A lead, not a verdict.

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
    internal static class JawaBenchMapCompTimer
    {
        internal const string HarmonyId = "mandrake.jawabench.mapcomptiming";
        internal static readonly Dictionary<Type, long[]> Acc = new Dictionary<Type, long[]>(); // calls, total, max (Stopwatch ticks)
        internal static volatile bool Armed;
        internal static int MainThreadId = -1;
        internal static int Depth;
        internal static long Foreign;

        // __state: -1 not counted (disarmed / foreign thread), -2 nested (depth taken, not timed), >= 0 start stamp.
        internal static void Pre(out long __state)
        {
            if (!Armed) { __state = -1; return; }
            if (Thread.CurrentThread.ManagedThreadId != MainThreadId) { Foreign++; __state = -1; return; }
            Depth++;
            __state = Depth == 1 ? Stopwatch.GetTimestamp() : -2;
        }

        internal static void Fin(MapComponent __instance, long __state)
        {
            if (__state == -1) return;
            Depth--;
            if (__state < 0 || __instance == null) return;
            long d = Stopwatch.GetTimestamp() - __state;
            Type t = __instance.GetType();
            if (!Acc.TryGetValue(t, out var a)) { a = new long[3]; Acc[t] = a; }
            a[0]++; a[1] += d; if (d > a[2]) a[2] = d;
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/map_comp_timing",
            Description =
                "TEST/DIAGNOSTIC. Times every MapComponent's MapComponentTick on the CURRENT map over the next N real " +
                "ticks: installs a prefix+finalizer timer on each distinct override, waits while the game runs at the " +
                "speed the CALLER set (unpause first; it never changes speed), then unpatches everything. Returns the " +
                "top components by total ms with ms per elapsed tick, max single call and the owning mod (packageId of " +
                "the mod whose loaded assemblies contain the type). Elapsed time: CPU, GC pauses and blocking all count, " +
                "so it is a lead, not a verdict.",
            ResultDescription =
                "success, ticksElapsed, realSeconds, patchedMethods, patchFailures[], sumMs, sumMsPerTick, " +
                "foreignThreadCalls, components[] of {type, assembly, packageId, calls, totalMs, msPerTick, maxMs}.")]
        public static async Task<object> MapCompTiming(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Real game ticks to sample (default 300).")] int ticks = 300,
            [ToolParameter(Description = "Give up after this many real seconds (default 120).")] int maxSeconds = 120,
            [ToolParameter(Description = "How many components to return, largest first (default 30).")] int top = 30)
        {
            if (ticks < 1) ticks = 1;
            var failures = new List<string>();
            int patched = 0, startTick = 0;
            var sw = Stopwatch.StartNew();
            try
            {
                object setup = await ctx.MainThread.InvokeAsync(() =>
                {
                    if (Current.Game == null || Find.CurrentMap == null) return Fail("No current map.");
                    var methods = new HashSet<MethodInfo>();
                    foreach (MapComponent c in Find.CurrentMap.components)
                    {
                        if (c == null) continue;
                        MethodInfo m = c.GetType().GetMethod("MapComponentTick",
                            BindingFlags.Public | BindingFlags.Instance, null, Type.EmptyTypes, null);
                        if (m != null && m.DeclaringType != typeof(MapComponent) && !m.IsAbstract) methods.Add(m);
                    }
                    JawaBenchMapCompTimer.Acc.Clear();
                    JawaBenchMapCompTimer.Depth = 0;
                    JawaBenchMapCompTimer.Foreign = 0;
                    JawaBenchMapCompTimer.MainThreadId = Thread.CurrentThread.ManagedThreadId;
                    try
                    {
                        var h = new Harmony(JawaBenchMapCompTimer.HarmonyId);
                        var pre = new HarmonyMethod(typeof(JawaBenchMapCompTimer).GetMethod("Pre", BindingFlags.Static | BindingFlags.NonPublic));
                        var fin = new HarmonyMethod(typeof(JawaBenchMapCompTimer).GetMethod("Fin", BindingFlags.Static | BindingFlags.NonPublic));
                        foreach (var m in methods)
                        {
                            try { h.Patch(m, prefix: pre, finalizer: fin); patched++; }
                            catch (Exception ex) { failures.Add(m.DeclaringType?.FullName + ": " + ex.GetType().Name + " " + ex.Message); }
                        }
                    }
                    catch (Exception ex) { return Fail("Harmony unavailable: " + ex.Message); }
                    startTick = Find.TickManager.TicksGame;
                    JawaBenchMapCompTimer.Armed = true;
                    return null;
                });
                if (setup != null) return setup;

                while (true)
                {
                    await Task.Delay(250, cancellationToken).ConfigureAwait(false);
                    int now = await ctx.MainThread.InvokeAsync(() => Find.TickManager?.TicksGame ?? startTick);
                    if (now - startTick >= ticks || sw.Elapsed.TotalSeconds >= maxSeconds) break;
                }

                return await ctx.MainThread.InvokeAsync(() =>
                {
                    JawaBenchMapCompTimer.Armed = false;
                    int elapsed = Math.Max(1, Find.TickManager.TicksGame - startTick);
                    double f = 1000.0 / Stopwatch.Frequency;
                    var asmToPkg = new Dictionary<Assembly, string>();
                    foreach (var mod in LoadedModManager.RunningModsListForReading)
                    {
                        if (mod.assemblies?.loadedAssemblies == null) continue;
                        foreach (var a in mod.assemblies.loadedAssemblies) if (!asmToPkg.ContainsKey(a)) asmToPkg[a] = mod.PackageId;
                    }
                    var rows = JawaBenchMapCompTimer.Acc.Select(kv => new
                    {
                        type = kv.Key.FullName,
                        assembly = kv.Key.Assembly.GetName().Name,
                        packageId = asmToPkg.TryGetValue(kv.Key.Assembly, out var p) ? p
                            : (kv.Key.Assembly == typeof(MapComponent).Assembly ? "ludeon (Assembly-CSharp)" : "?"),
                        calls = kv.Value[0],
                        totalMs = Math.Round(kv.Value[1] * f, 2),
                        msPerTick = Math.Round(kv.Value[1] * f / elapsed, 3),
                        maxMs = Math.Round(kv.Value[2] * f, 2),
                    }).OrderByDescending(r => r.totalMs).ToList();
                    double sum = rows.Sum(r => r.totalMs);
                    // telemetry design 3.6: the reply is also persisted as `mapcomp` rows (one per returned component, one
                    // `run` id per call) so the number stops living in prose. Best effort: a stopped writer writes nothing.
                    int persisted = 0;
                    if (JawaBenchTpsWriter.Running)
                    {
                        long run = JawaBenchTpsWriter.Clock.ElapsedMilliseconds;
                        foreach (var r in rows.Take(Math.Max(1, top)))
                            if (JawaBenchTpsWriter.Enqueue("mapcomp", "\"run\":" + run + ",\"type\":" + JawaBenchTpsWriter.Json(r.type) +
                                    ",\"mod\":" + JawaBenchTpsWriter.Json(r.packageId) + ",\"assembly\":" + JawaBenchTpsWriter.Json(r.assembly) +
                                    ",\"msPerTick\":" + JawaBenchTpsMath.F(r.msPerTick, 3) + ",\"calls\":" + r.calls +
                                    ",\"maxMs\":" + JawaBenchTpsMath.F(r.maxMs, 2) + ",\"totalMs\":" + JawaBenchTpsMath.F(r.totalMs, 2) +
                                    ",\"ticks\":" + elapsed + ",\"tickFrom\":" + startTick + ",\"realS\":" + JawaBenchTpsMath.F(sw.Elapsed.TotalSeconds, 1)) >= 0)
                                persisted++;
                    }
                    return (object)new
                    {
                        success = true,
                        ticksElapsed = elapsed,
                        realSeconds = Math.Round(sw.Elapsed.TotalSeconds, 1),
                        patchedMethods = patched,
                        patchFailures = failures,
                        sumMs = Math.Round(sum, 1),
                        sumMsPerTick = Math.Round(sum / elapsed, 2),
                        foreignThreadCalls = JawaBenchMapCompTimer.Foreign,
                        componentsTimed = rows.Count,
                        recordRows = persisted,
                        components = rows.Take(Math.Max(1, top)).ToList(),
                    };
                });
            }
            finally
            {
                JawaBenchMapCompTimer.Armed = false;
                try { await ctx.MainThread.InvokeAsync(() => { new Harmony(JawaBenchMapCompTimer.HarmonyId).UnpatchAll(JawaBenchMapCompTimer.HarmonyId); return 0; }); }
                catch { }
            }
        }
    }
}
#endif
