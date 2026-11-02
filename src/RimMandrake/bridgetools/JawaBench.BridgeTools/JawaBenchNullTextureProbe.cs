// JawaBenchNullTextureProbe.cs - who passes a null texture to GUI.DrawTexture?
// (WORLD_NULLTEX_FLOOD_HUNT_STACKLESS_SO_FAR)
//
// THE SYMPTOM. On the full list, Player.log fills with "null texture passed to GUI.DrawTexture"
// (19,519 lines in the worldlook3 load, which hit Verse's message cap twice; 77 in the next load).
// Unity writes that line through Debug.LogWarning with no managed stack, so the log cannot name
// the caller.
//
// WHERE THE LINE COMES FROM (decompiled UnityEngine.IMGUIModule, RimWorld 1.6). Every public
// GUI.DrawTexture overload funnels into ONE internal 12-argument overload:
//   (Rect, Texture, ScaleMode, bool, float, Color, Color, Color, Color, Vector4, Vector4, bool)
// which does: CheckOnGUI; return unless Event.current.type == Repaint; if (image == null)
// { Debug.LogWarning("null texture passed to GUI.DrawTexture"); return; }.
// This probe is a Harmony prefix on that overload that records the managed stack under the
// SAME condition (Repaint and Unity-null image), so each line it counts is one logged line.
// It never changes what the engine does: the prefix always returns true.
//
// THE OFFLINE SUSPECT (to be confirmed or refuted by this probe, not assumed): RimThemes'
// aRandomKiwi.RimThemes.UI_BackgroundMain_Patch.Prefix and LoaderGM draw VideoPlayer.texture
// with no null check, and VideoPlayer.texture is null until the video has a frame. Findings and
// the offline/live proof: src/RimMandrake/bridgetools/nulltex_probe.py.
//
// INSTALL. Lazily on the first jawa/ call (JawaBenchInit), like the arg guard: RimBridge reads
// companion tools from metadata, so nothing here runs earlier. ARMED by default. Recording
// costs a StackTrace only on a null call; the prefix on a non-null call is one Unity null check.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using HarmonyLib;
using RimBridgeServer.Sdk;
using UnityEngine;
using Verse;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchNullTextureProbe
    {
        internal static readonly Type[] TargetArgs =
        {
            typeof(Rect), typeof(Texture), typeof(ScaleMode), typeof(bool), typeof(float),
            typeof(Color), typeof(Color), typeof(Color), typeof(Color),
            typeof(Vector4), typeof(Vector4), typeof(bool)
        };
        internal const string Target = "UnityEngine.GUI.DrawTexture(Rect, Texture, ScaleMode, bool, float, Color x4, Vector4, Vector4, bool)";
        internal const int MaxStacks = 64;     // distinct stacks kept; later new ones only counted
        internal const int MaxFrames = 14;     // frames kept per stack, after the GUI/Harmony frames

        internal static bool Installed;
        internal static string InstallError;
        internal static volatile bool Armed = true;
        internal static long NullCalls;        // every recorded null call, kept stack or not
        internal static long DroppedStacks;    // null calls whose (new) stack did not fit MaxStacks
        internal static long RecordErrors;
        internal static string LastRecordError;
        internal static float InstalledAt = -1f;
        // Seconds since this class loaded. Not Time.realtimeSinceStartup: Install and Snapshot run on the
        // bridge's worker thread, where a Unity API may refuse to answer.
        private static readonly Stopwatch Clock = Stopwatch.StartNew();
        internal static float Now => (float)Clock.Elapsed.TotalSeconds;

        internal sealed class Entry
        {
            public string Caller;
            public List<string> Frames;
            public long Count;
            public float FirstAt, LastAt;
            public readonly Dictionary<string, long> ByProgramState = new Dictionary<string, long>();
            public long DuringLongEvent;
        }

        internal static readonly Dictionary<string, Entry> ByStack = new Dictionary<string, Entry>();
        internal static readonly object Gate = new object();
        private static bool _attempted;

        internal static void Install()
        {
            lock (Gate)
            {
                if (_attempted) return;
                _attempted = true;
                try
                {
                    var m = AccessTools.Method(typeof(GUI), "DrawTexture", TargetArgs);
                    if (m == null)
                    {
                        InstallError = "overload " + Target + " not found - Unity may have changed the funnel";
                        Log.Warning("[JawaBench] null-texture probe NOT installed: " + InstallError);
                        return;
                    }
                    new Harmony("mandrake.jawabench.nulltextureprobe").Patch(m, prefix: new HarmonyMethod(
                        typeof(JawaBenchNullTextureProbe).GetMethod(nameof(Prefix), BindingFlags.Static | BindingFlags.NonPublic)));
                    Installed = true;
                    InstalledAt = Now;
                    Log.Message("[JawaBench] null-texture probe installed on " + Target + ", armed=" + Armed +
                                ". Read it with jawa/nulltex_probe.");
                }
                catch (Exception e)
                {
                    InstallError = e.GetType().Name + ": " + e.Message;
                    Log.Warning("[JawaBench] null-texture probe NOT installed: " + InstallError);
                }
            }
        }

        // Harmony binds 'image' by parameter name; the engine's own test is Unity's == null,
        // which also counts a destroyed texture, so this uses the same operator.
        private static void Prefix(Texture image)
        {
            if (!Armed || image != null) return;
            try
            {
                var ev = Event.current;
                if (ev == null || ev.type != EventType.Repaint) return;
                Record();
            }
            catch (Exception e)
            {
                Interlocked.Increment(ref RecordErrors);
                LastRecordError = e.GetType().Name + ": " + e.Message;
            }
        }

        // True for frames that are the draw call itself: GUI, the Harmony replacement (its
        // DeclaringType is null or a DMD wrapper), HarmonyLib, and this probe.
        internal static bool IsPlumbing(MethodBase m)
        {
            if (m == null) return true;
            var t = m.DeclaringType;
            if (t == null) return true;
            string n = t.FullName ?? t.Name ?? "";
            return n == "UnityEngine.GUI" || n.StartsWith("HarmonyLib.", StringComparison.Ordinal)
                   || n.StartsWith("MonoMod.", StringComparison.Ordinal)
                   || t == typeof(JawaBenchNullTextureProbe)
                   || (m.Name ?? "").StartsWith("DMD<", StringComparison.Ordinal);
        }

        internal static string Describe(MethodBase m)
        {
            if (m == null) return "<unknown>";
            var t = m.DeclaringType;
            string asm = "";
            try { asm = t?.Assembly.GetName().Name ?? ""; } catch { }
            return (t != null ? t.FullName : "<dynamic>") + "." + m.Name + (asm.Length > 0 ? " [" + asm + "]" : "");
        }

        private static void Record()
        {
            Interlocked.Increment(ref NullCalls);
            var frames = new StackTrace(1, false).GetFrames() ?? new StackFrame[0];
            var kept = new List<string>(MaxFrames);
            string caller = null;
            foreach (var f in frames)
            {
                var m = f.GetMethod();
                if (caller == null && IsPlumbing(m)) continue;
                string d = Describe(m);
                if (caller == null) caller = d;
                kept.Add(d);
                if (kept.Count >= MaxFrames) break;
            }
            if (caller == null) caller = "<no managed caller above GUI.DrawTexture>";
            string key = string.Join(" <- ", kept);
            float now = Now;
            string state = "unknown";
            bool longEvent = false;
            try { state = Current.ProgramState.ToString(); } catch { }
            try { longEvent = LongEventHandler.AnyEventNowOrWaiting; } catch { }
            lock (Gate)
            {
                if (!ByStack.TryGetValue(key, out var e))
                {
                    if (ByStack.Count >= MaxStacks) { DroppedStacks++; return; }
                    e = new Entry { Caller = caller, Frames = kept, FirstAt = now };
                    ByStack[key] = e;
                }
                e.Count++;
                e.LastAt = now;
                e.ByProgramState.TryGetValue(state, out var c);
                e.ByProgramState[state] = c + 1;
                if (longEvent) e.DuringLongEvent++;
            }
        }

        internal static object Snapshot(int top)
        {
            lock (Gate)
            {
                var rows = ByStack.Values.OrderByDescending(e => e.Count).Take(Math.Max(1, top)).Select(e => (object)new
                {
                    count = e.Count,
                    caller = e.Caller,
                    frames = e.Frames,
                    firstAt = e.FirstAt,
                    lastAt = e.LastAt,
                    byProgramState = e.ByProgramState.ToDictionary(kv => kv.Key, kv => kv.Value),
                    duringLongEvent = e.DuringLongEvent
                }).ToList();
                var callers = ByStack.Values.GroupBy(e => e.Caller)
                    .Select(g => new { caller = g.Key, count = g.Sum(e => e.Count) })
                    .OrderByDescending(x => x.count).ToList();
                return new
                {
                    installed = Installed,
                    installError = InstallError,
                    target = Target,
                    armed = Armed,
                    installedAt = InstalledAt,
                    now = Now,
                    nullCalls = Interlocked.Read(ref NullCalls),
                    distinctStacks = ByStack.Count,
                    droppedStacks = DroppedStacks,
                    recordErrors = Interlocked.Read(ref RecordErrors),
                    lastRecordError = LastRecordError,
                    byCaller = callers,
                    stacks = rows
                };
            }
        }

        internal static void Reset()
        {
            lock (Gate)
            {
                ByStack.Clear();
                Interlocked.Exchange(ref NullCalls, 0);
                DroppedStacks = 0;
                Interlocked.Exchange(ref RecordErrors, 0);
                LastRecordError = null;
            }
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/nulltex_probe",
            Description =
                "Name the managed caller behind every 'null texture passed to GUI.DrawTexture' warning " +
                "(Player.log carries no stack for it). A Harmony prefix on Unity's internal 12-argument " +
                "GUI.DrawTexture - the overload every public one funnels into and the only place the warning " +
                "is written - records the stack of each null call under the engine's own condition (Repaint, " +
                "Unity-null image). Installed and ARMED on the first jawa/ call of the session, so it sees " +
                "nothing before that. 'get' (default) reads; 'arm' / 'disarm' toggle recording; 'reset' clears " +
                "the counts. READ 'installed' FIRST: installed=false means nullCalls=0 is blindness, not health.",
            ResultDescription =
                "installed, installError, armed, nullCalls, distinctStacks, droppedStacks, byCaller (caller -> " +
                "count, the first frame above GUI/Harmony), stacks (top N: count, caller, frames, " +
                "byProgramState, duringLongEvent, firstAt/lastAt/installedAt/now in seconds on the probe's own clock).")]
        public static Task<object> NullTexProbe(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'get' (default), 'arm', 'disarm' or 'reset'.")]
            string action = "get",
            [ToolParameter(Description = "How many of the most frequent stacks to return (default 10).")]
            int top = 10)
        {
            cancellationToken.ThrowIfCancellationRequested();
            var act = (action ?? "get").Trim().ToLowerInvariant();
            if (act != "get" && act != "arm" && act != "disarm" && act != "reset")
                return Task.FromResult(Fail("Unknown action '" + action + "'. Use 'get', 'arm', 'disarm' or 'reset'."));
            JawaBenchNullTextureProbe.Install();
            if (!JawaBenchNullTextureProbe.Installed && act != "get")
                return Task.FromResult(Fail("The probe is not installed, so '" + act + "' would do nothing.",
                    new { installError = JawaBenchNullTextureProbe.InstallError }));
            if (act == "arm") JawaBenchNullTextureProbe.Armed = true;
            else if (act == "disarm") JawaBenchNullTextureProbe.Armed = false;
            else if (act == "reset") JawaBenchNullTextureProbe.Reset();
            return Task.FromResult(JawaBenchNullTextureProbe.Snapshot(top));
        }
    }
}
