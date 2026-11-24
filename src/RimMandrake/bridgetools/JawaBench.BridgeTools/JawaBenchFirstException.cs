// JawaBenchFirstException.cs - jawa/first_exception: the first exception of the session, kept through any log flood.
// Page: design/specs/2026-11-23-first-exception-tap/boundary.md. Pure rules: JawaBenchFirstExceptionCore.cs.
//
// Engine facts, read from decompiled 1.6 through RimSage on 2026-11-23 (Verse.Log): Error and ErrorOnce return at once when
// reachedMaxMessagesLimit or a LogLock is on, so a hook IN FRONT of them still sees the text; at 10,000 messages the game
// also sets Debug.unityLogger.logEnabled = false; TickList.Tick catches a thing's exception and sends ex.ToString() to
// Log.Error (dev mode) or Log.ErrorOnce.
// A prefix on the logger must never log and never throw: every body is try/catch and the original always runs.
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
using E = JawaBench.BridgeTools.JawaBenchFirstExceptionCore;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchFirstException
    {
        internal const string HarmonyId = "mandrake.jawabench.firstexception";
        internal static readonly E.Tap Tap = new E.Tap();
        internal static string ArmedBy, ArmedUtc, InstallError, BeforeArm;
        internal static bool HooksOn, UnityOn;
        internal static string CapHitUtc, CapHitWindow;
        private static bool _attempted;
        private static readonly object Gate = new object();
        [ThreadStatic] private static E.Roads _roads;
        private static E.Roads Roads => _roads ?? (_roads = new E.Roads());
        private static FieldInfo _fReached, _fDisablers;

        /// <summary>At bridge registration (main thread). Off the main thread only the Unity channel is taken now and the hooks
        /// wait for the main thread: patching a method that another thread may be running is not attempted.</summary>
        internal static void Install(string by)
        {
            lock (Gate)
            {
                if (!UnityOn) try { Application.logMessageReceivedThreaded += OnUnity; UnityOn = true; } catch (Exception e) { InstallError = "unity channel: " + e.Message; }
                if (_attempted) return;
                if (!UnityData.IsInMainThread) { try { LongEventHandler.ExecuteWhenFinished(() => Install(by)); } catch { } return; }
                _attempted = true;
                ArmedBy = by; ArmedUtc = DateTime.UtcNow.ToString("o"); Tap.WindowUtc = ArmedUtc;
                try
                {
                    var msgs = Log.Messages.Where(m => m.type == LogMessageType.Error).ToList();
                    BeforeArm = msgs.Count + " error message(s) in the game's log window when the tap armed (the window keeps only its last messages)" +
                                (msgs.Count > 0 ? "; first kept: " + E.Clip(msgs[0].text) : "");
                }
                catch (Exception e) { BeforeArm = "could not read the game's log window: " + e.GetType().Name; }
                try
                {
                    var h = new Harmony(HarmonyId);
                    HarmonyMethod Hm(string n) => new HarmonyMethod(typeof(JawaBenchFirstException).GetMethod(n, BindingFlags.Static | BindingFlags.NonPublic)) { priority = Priority.First };
                    h.Patch(AccessTools.Method(typeof(Log), nameof(Log.Error), new[] { typeof(string) }), prefix: Hm(nameof(ErrorPre)), finalizer: Hm(nameof(ErrorFin)));
                    h.Patch(AccessTools.Method(typeof(Log), nameof(Log.ErrorOnce), new[] { typeof(string), typeof(int) }), prefix: Hm(nameof(OncePre)), finalizer: Hm(nameof(OnceFin)));
                    h.Patch(AccessTools.Method(typeof(Log), nameof(Log.ResetMessageCount), Type.EmptyTypes), prefix: Hm(nameof(ResetPre)));
                    _fReached = AccessTools.Field(typeof(Log), "reachedMaxMessagesLimit");
                    _fDisablers = AccessTools.Field(typeof(Log), "logDisablers");
                }
                catch (Exception e) { InstallError = "hooks: " + e.GetType().Name + ": " + e.Message; }
            }
        }

        /// <summary>Read from Harmony, not from a flag: are our prefixes on both methods now?</summary>
        internal static string ReadHooks()
        {
            try
            {
                foreach (var m in new[] { AccessTools.Method(typeof(Log), nameof(Log.Error), new[] { typeof(string) }), AccessTools.Method(typeof(Log), nameof(Log.ErrorOnce), new[] { typeof(string), typeof(int) }) })
                {
                    var i = m == null ? null : Harmony.GetPatchInfo(m);
                    if (i == null || !i.Prefixes.Any(p => p.owner == HarmonyId)) { HooksOn = false; return (m?.Name ?? "a Log method") + " has no hook of ours" + (InstallError != null ? " (" + InstallError + ")" : ""); }
                }
                HooksOn = true;
                return null;
            }
            catch (Exception e) { HooksOn = false; return "the hooks could not be read: " + e.GetType().Name + ": " + e.Message; }
        }

        private static void Fill(E.Entry e)
        {
            e.Utc = DateTime.UtcNow.ToString("o");
            try { e.UptimeS = Math.Round(JawaBenchTpsWatchdog.Now, 3); } catch { }
            try { e.Tick = Current.Game?.tickManager != null ? Current.Game.tickManager.TicksGame : (int?)null; } catch { }
            try { e.ProgramState = Current.ProgramState.ToString(); } catch { }
            try { e.Thread = UnityData.IsInMainThread ? "main" : "worker:" + Thread.CurrentThread.ManagedThreadId; } catch { }
            if (e.Stack == null) e.Stack = new StackTrace(4, false).ToString();
        }

        private static void ErrorPre(string text, out bool __state)
        {
            __state = false;
            try
            {
                JawaBenchTpsWatchdog.NoteRootException(text);
                Roads.EnterError(); __state = true; Tap.Note("Log.Error", text, false, false, Fill);
            }
            catch { }
        }
        private static void ErrorFin(bool __state)
        {
            try { if (__state) Roads.ExitError(); } catch { }      // an orphan (our prefix was skipped) leaves the depth alone
        }
        private static void OncePre(out bool __state)
        {
            __state = false;
            try { Roads.EnterOnce(); __state = true; } catch { }
        }
        private static void OnceFin(string text, bool __state)
        {
            try { if (__state) { if (Roads.ExitOnce()) Tap.Note("Log.ErrorOnce (kept silent by the game)", text, false, true, Fill); } } catch { }
        }

        /// <summary>The cap ends here (Log.Clear and the log-revive tools come through it): keep that it was reached. The game's own
        /// "Reached max messages limit" warning is logged inside Unity's callback and does not reach ours (live, 2026-11-23).</summary>
        private static void ResetPre() { try { if (Reached() == true) NoteCap(); } catch { } }
        private static bool? Reached() { try { return _fReached == null ? (bool?)null : (bool)_fReached.GetValue(null); } catch { return null; } }
        private static void NoteCap()
        {
            var now = DateTime.UtcNow.ToString("o");
            if (CapHitUtc == null) CapHitUtc = now;
            if (CapHitWindow == null) CapHitWindow = now;
        }

        private static void OnUnity(string condition, string stackTrace, LogType type)
        {
            try
            {
                if (type != LogType.Exception && type != LogType.Error && type != LogType.Assert) return;
                if (Roads.UnityIsACopy) return;
                Tap.Note("unity " + type, condition, type == LogType.Exception, false, e => { e.Stack = stackTrace; Fill(e); });
            }
            catch { }
        }

        internal static List<string> Blind()
        {
            var b = new List<string>();
            if (!UnityOn) b.Add("the Unity channel is not subscribed");
            bool? reached = Reached(), logOn = null; int? dis = null;
            if (reached == true) NoteCap();
            try { if (_fDisablers != null) dis = (int)_fDisablers.GetValue(null); } catch { }
            try { logOn = UnityEngine.Debug.unityLogger.logEnabled; } catch { }
            if (logOn == null) b.Add("Unity's logger state could not be read");
            else if (logOn == false) b.Add("Unity's logger is off" + (reached == true ? " (the game reached its 10,000-message cap)" : "") + ": a Unity-only exception is not seen; Log.Error still is");
            if (reached == null) b.Add("the game's message cap could not be read");
            if (dis == null) b.Add("the game's log lock could not be read");
            if (CapHitWindow != null) b.Add("the 10,000-message cap was reached in this window (seen at " + CapHitWindow + "): a Unity-only exception after it may be missing");
            try { var i = Harmony.GetPatchInfo(AccessTools.Method(typeof(Log), nameof(Log.ResetMessageCount), Type.EmptyTypes)); if (i == null || !i.Prefixes.Any(x => x.owner == HarmonyId)) b.Add("a cap that was reached and reset would not be seen (no hook on Log.ResetMessageCount)"); }
            catch (Exception e) { b.Add("the hook on Log.ResetMessageCount could not be read: " + e.GetType().Name); }
            return b;
        }

        internal static object Row(E.Entry e) => e == null ? null : new
        {
            seq = e.Seq, isException = e.IsException, source = e.Source, tick = e.Tick, programState = e.ProgramState, utc = e.Utc, uptimeS = e.UptimeS,
            thread = e.Thread, repeats = e.Repeats, text = e.Text, stack = e.Stack,
        };
    }

    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/first_exception",
            Description =
                "The FIRST exception (and the first plain error) of the session and of the open window, kept through any log flood: " +
                "a hook in front of Verse.Log.Error / ErrorOnce (before the game's 10,000-message stop) plus Unity's log callback. The tap " +
                "arms itself at bridge registration; the cold load before that is NOT covered (beforeArm says what the log window held). " +
                "action=read (default) | arm (open a new window named `label`; the session's first is kept) | plant (TEST profile only: really throw one " +
                "known exception, then log `flood` lines). Act on `state` of the window: SEEN; NONE_SEEN; NONE_SEEN_PARTIAL (blind[] names the channel " +
                "that could have missed one); NOT_ARMED. Only NONE_SEEN means no exception was logged. Not seen: an exception that nobody logs, or one logged as a warning.",
            ResultDescription =
                "success, state, armed, armedUtc, window{label, sinceUtc, exceptions, errors, firstException, firstError}, session{exceptions, errors, " +
                "firstException, firstError}, kept[] (up to 16 different exceptions, in order), distinct, notKept, silenced, blind[], beforeArm. Each entry: " +
                "seq, source, tick, programState, utc, uptimeS, thread, repeats, text, stack.")]
        public static async Task<object> FirstException(
            IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "read | arm | plant", DefaultValue = "read")] string action = "read",
            [ToolParameter(Description = "arm: the window's name (a scene or a visit)", DefaultValue = null)] string label = null,
            [ToolParameter(Description = "plant: 'caught' (thrown in a post-long-event action, which the game catches and logs) | 'unity' (Debug.LogException) | 'unhook' (take the hooks named by label off, to see that the readers say so)", DefaultValue = "caught")] string kind = "caught",
            [ToolParameter(Description = "plant: then log this many different messages (0-12000) to flood the log", DefaultValue = 0)] int flood = 0)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                var a = (action ?? "read").Trim().ToLowerInvariant();
                if (a != "read" && a != "arm" && a != "plant") return Fail("action must be read, arm or plant");
                JawaBenchFirstException.Install("tool-call");
                if (a == "arm")
                {
                    JawaBenchFirstException.Tap.NewWindow(string.IsNullOrWhiteSpace(label) ? "unnamed" : label.Trim(), DateTime.UtcNow.ToString("o"));
                    JawaBenchFirstException.CapHitWindow = null;
                }
                if (a == "plant")
                {
                    if (JawaBenchCompanionSafety.CurrentPolicy.DenyCampaignFamilies) return Fail("plant is refused outside the test profile: it throws a real exception");
                    if (flood < 0 || flood > 12000) return Fail("flood must be 0 to 12000");
                    var k = (kind ?? "").Trim().ToLowerInvariant();
                    if (k == "caught") LongEventHandler.ExecuteWhenFinished(PlantedThrow);
                    else if (k == "unity") { try { PlantedThrow(); } catch (Exception e) { UnityEngine.Debug.LogException(e); } }
                    else if (k == "unhook")
                    {
                        var id = (label ?? "").Trim();
                        if (id != JawaBenchFirstException.HarmonyId && id != JawaBenchCalm.HarmonyId)
                            return Fail("unhook takes the hooks of this tap or of the calm map off: label must be " + JawaBenchFirstException.HarmonyId + " or " + JawaBenchCalm.HarmonyId);
                        new Harmony(id).UnpatchAll(id);
                    }
                    else return Fail("kind must be caught, unity or unhook");
                    for (int i = 0; i < flood; i++) Log.Message("[JawaBench] planted flood line " + i);
                }
                var why = JawaBenchFirstException.ReadHooks();
                bool armed = why == null;
                var blind = JawaBenchFirstException.Blind();
                var t = JawaBenchFirstException.Tap;
                return (object)new
                {
                    success = true, action = a,
                    state = E.State(armed, t.WindowException != null, blind),
                    armed, notArmedWhy = why, armedBy = JawaBenchFirstException.ArmedBy, armedUtc = JawaBenchFirstException.ArmedUtc,
                    window = new { label = t.Window, sinceUtc = t.WindowUtc, exceptions = t.WindowExceptions, errors = t.WindowErrors,
                                   firstException = JawaBenchFirstException.Row(t.WindowException), firstError = JawaBenchFirstException.Row(t.WindowError) },
                    session = new { exceptions = t.Exceptions, errors = t.Errors, firstException = JawaBenchFirstException.Row(t.SessionException),
                                    firstError = JawaBenchFirstException.Row(t.SessionError) },
                    kept = t.Kept().Select(e => new { seq = e.Seq, tick = e.Tick, repeats = e.Repeats, source = e.Source, key = e.Key }).ToList(),
                    distinct = t.DistinctKeys, notKept = t.NotKept, keysDropped = t.KeysDropped, silenced = t.Silenced,
                    blind, capHitUtc = JawaBenchFirstException.CapHitUtc, beforeArm = JawaBenchFirstException.BeforeArm ?? "not read",
                    ticksGame = TicksGameSafe(),
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        private static void PlantedThrow() => throw new InvalidOperationException("JawaBench planted exception (jawa/first_exception action=plant)");
    }
}
