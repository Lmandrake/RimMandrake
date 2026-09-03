// JawaBenchLogAutoOpenSuppress.cs - stop the error/warning log window stealing the
// screen on every red error, without turning dev mode off.
//
// DEV_LOG_AUTOOPEN_SUPPRESS_1.
//
// Owner, 2026-09-02: "Man I wish the Autoopen of the error log was set to False by
// default". There is no vanilla pref for it, measured: Verse.Log.Error's own auto-open
// gate is `!PlayDataLoader.Loaded || Prefs.DevMode` - dev mode alone decides it, and
// the only pref in this area (Prefs.OpenLogOnWarnings) gates warnings, not errors. So
// the vanilla choices are "dev mode off" (not an option for us) or "the window opens on
// every error" - neither of which the owner wants.
//
// The fix: a Harmony prefix on Verse.Log.TryOpenLogWindow that returns false (skips the
// original) while suppression is enabled. TryOpenLogWindow just calls
// EditWindow_Log.TryAutoOpen(); the debug menu's manual toggle (DebugWindowsOpener.cs)
// calls Find.WindowStack.Add(new EditWindow_Log()) directly and never goes through
// TryOpenLogWindow at all - confirmed from 1.6 source before writing this - so a blanket
// prefix here cannot touch the by-hand path.
//
// ⚠️ TryOpenLogWindow has three callers (Log.cs): the error path, the
// Prefs.OpenLogOnWarnings-gated warning path, and PostMessage (fires whenever
// Log.openOnMessage is set, from either). A blanket prefix suppresses all three. That is
// the intended behaviour - the owner's ask was "the auto-open", not "just errors" - and
// it is stated here rather than left for someone to discover from a silent difference.

using System;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using HarmonyLib;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    /// <summary>
    /// Harmony contact point, isolated on the same discipline as JawaBenchArgGuard: no
    /// Harmony type touched outside Install()/Prefix, both try/catch-guarded, so an
    /// absent 0Harmony only fails when Install() actually runs.
    /// </summary>
    internal static class JawaBenchLogAutoOpenSuppress
    {
        internal const string TargetType = "Verse.Log";
        internal const string TargetMethod = "TryOpenLogWindow";

        internal static bool Installed;
        internal static string InstallError;      // null when Installed

        /// <summary>Default ON - the owner's own wish was "set to False by default",
        /// i.e. suppression on by default. One toggle away from being off again.</summary>
        internal static bool Suppressed = true;

        internal static int Suppressions;          // auto-open calls actually skipped

        private static readonly object Gate = new object();
        private static bool _attempted;

        internal static void Install()
        {
            lock (Gate)
            {
                if (_attempted) return;
                _attempted = true;
                try
                {
                    var t = AccessTools.TypeByName(TargetType);
                    if (t == null)
                    {
                        InstallError = "type '" + TargetType + "' not found in any loaded assembly";
                        Log.Warning("[JawaBench] log auto-open suppressor NOT installed: " + InstallError +
                                    " - the error log will keep popping on every red error.");
                        return;
                    }
                    var m = AccessTools.Method(t, TargetMethod);
                    if (m == null)
                    {
                        InstallError = "method '" + TargetType + "." + TargetMethod +
                                       "' not found - upstream may have renamed or inlined it.";
                        Log.Warning("[JawaBench] log auto-open suppressor NOT installed: " + InstallError);
                        return;
                    }

                    var harmony = new Harmony("mandrake.jawabench.logautoopensuppress");
                    harmony.Patch(m, prefix: new HarmonyMethod(
                        typeof(JawaBenchLogAutoOpenSuppress).GetMethod(nameof(Prefix),
                            BindingFlags.Static | BindingFlags.NonPublic)));

                    Installed = true;
                    Log.Message("[JawaBench] log auto-open suppressor installed on " + TargetType + "." + TargetMethod +
                                " - suppressed=" + Suppressed +
                                ". The debug menu's manual log window is a separate code path and is unaffected.");
                }
                catch (Exception e)
                {
                    InstallError = e.GetType().Name + ": " + e.Message;
                    Log.Warning("[JawaBench] log auto-open suppressor NOT installed: " + InstallError);
                }
            }
        }

        /// <summary>Returning false skips Verse.Log.TryOpenLogWindow's own body entirely
        /// - EditWindow_Log.TryAutoOpen() never runs. Never throws: a suppressor that
        /// breaks logging would be worse than the popup it removes.</summary>
        private static bool Prefix()
        {
            try
            {
                if (!Suppressed) return true;
                Interlocked.Increment(ref Suppressions);
                return false;
            }
            catch
            {
                return true;
            }
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/log_autoopen_suppress",
            Description =
                "Suppress or restore the dev-mode auto-open of the error/warning log window " +
                "(Verse.Log.TryOpenLogWindow) - no vanilla pref exists for this, measured against " +
                "1.6 source; dev mode alone gates it. Backed by a Harmony prefix, suppressed by " +
                "default. The debug menu's own manual toggle is a SEPARATE code path " +
                "(DebugWindowsOpener) and always still works by hand regardless of this setting. " +
                "'get' (default) reports state; 'suppress' turns the auto-open off; 'restore' " +
                "turns it back to vanilla behaviour. READ 'installed' FIRST - the patch target is " +
                "a private/internal engine method and if upstream renamed it this reports nothing " +
                "while nothing is wrong with the call.",
            ResultDescription =
                "installed, installError, suppressed, and suppressions (auto-open calls actually " +
                "skipped this session). installed=false means the toggle does nothing - the log " +
                "will keep popping regardless of 'suppressed'.")]
        public static async Task<object> LogAutoOpenSuppress(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'get' (default), 'suppress' or 'restore'.")]
            string action = "get")
        {
            // Deliberately not inside MainThread.InvokeAsync - this reads/writes this
            // assembly's own static toggle, nothing that touches a Map or Pawn.
            cancellationToken.ThrowIfCancellationRequested();

            var act = (action ?? "get").Trim().ToLowerInvariant();
            if (act != "get" && act != "suppress" && act != "restore")
                return Fail("Unknown action '" + action + "'. Use 'get', 'suppress' or 'restore'.");

            if (act == "suppress" || act == "restore")
            {
                if (!JawaBenchLogAutoOpenSuppress.Installed)
                    return Fail("The suppressor is not installed, so this toggle would do nothing. " +
                                "This is a refusal, not a silent no-op.",
                        new { installError = JawaBenchLogAutoOpenSuppress.InstallError,
                              target = JawaBenchLogAutoOpenSuppress.TargetType + "." + JawaBenchLogAutoOpenSuppress.TargetMethod });
                JawaBenchLogAutoOpenSuppress.Suppressed = (act == "suppress");
            }

            return await Task.FromResult<object>(new
            {
                success = true,
                action = act,
                installed = JawaBenchLogAutoOpenSuppress.Installed,
                installError = JawaBenchLogAutoOpenSuppress.InstallError,
                target = JawaBenchLogAutoOpenSuppress.TargetType + "." + JawaBenchLogAutoOpenSuppress.TargetMethod,
                suppressed = JawaBenchLogAutoOpenSuppress.Suppressed,
                suppressions = JawaBenchLogAutoOpenSuppress.Suppressions,
                note = JawaBenchLogAutoOpenSuppress.Installed
                    ? (JawaBenchLogAutoOpenSuppress.Suppressed
                        ? "Auto-open is suppressed. The debug menu's manual log window still works by hand."
                        : "Auto-open behaves as vanilla - the log window pops on every red error again.")
                    : "NOT INSTALLED - the log window will keep auto-popping regardless of 'suppressed'."
            }).ConfigureAwait(false);
        }
    }
}
