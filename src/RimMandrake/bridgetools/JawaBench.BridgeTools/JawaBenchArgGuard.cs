// JawaBenchArgGuard.cs - make the bridge's silently dropped parameters VISIBLE.
//
// BRIDGE_DROPS_UNKNOWN_PARAMS_1.
//
// 🔴 THE DEFECT, MEASURED IN THE HOST'S OWN IL, 2026-08-27
// ========================================================
// RimBridgeServer.AnnotatedExtensionCapabilityProvider.BindArguments
//     private static object[] BindArguments(
//         MethodInfo method,
//         IReadOnlyDictionary<string, object> arguments,
//         RimBridgeServer.Sdk.IRimBridgeContext sdkContext,
//         CancellationToken cancellationToken)                      RVA 0x3fb28
//
// It iterates `method.GetParameters()` and, per parameter, calls
// `arguments.TryGetValue(param.Name, out v)`. It NEVER enumerates `arguments`, and
// the whole 90-instruction body contains no count comparison between the two. So a
// JSON key matching no declared [ToolParameter] is never read, never counted and
// never reported - for every tool on the bridge, not just ours.
//
// What that costs, measured, both on live calls:
//   new_allowed_area   the parameter is `label`. Passing `name` gave a default
//                      "Area 3" and a cheerful success.
//   stop_job           the parameter is `mode`. Passing `action: "StopAll"` ran
//                      `endcurrent` instead, and only that tool's own before/after
//                      read-back showed it.
// ⇒ A wrong parameter name is caught ONLY when the tool then misses a REQUIRED
// field. Wherever a sensible default exists you get a call that succeeds and does
// something else.
//
// ⛔ THE CHEAP FIX DOES NOT EXIST - DO NOT GO LOOKING FOR IT AGAIN.
// A full field/property census of RimBridgeServer.Sdk.IRimBridgeContext and its sole
// implementation RimBridgeServer.RimBridgeContext returns exactly
//     OperationId · CapabilityId · Tools · Game · MainThread
// and no raw-argument dictionary. A [Tool] method therefore CANNOT inspect its own
// unknown keys through ctx. Harmony on BindArguments is the only route, because that
// is the one place the full `arguments` dictionary and the declared parameter names
// are simultaneously in scope.
//
// 🔑 REPORT, DO NOT REFUSE - and that is a deliberate default, not timidity.
// This sits in the SHARED binder, so refusing would change behaviour for every tool
// on the bridge at once, including callers that have been passing a stray key and
// getting away with it. So: record by default, and let a caller turn refusal on
// explicitly once a session has shown what actually surfaces.
//
// ⚠️ THREE THINGS THIS CANNOT DO, STATED SO NOBODY READS MORE INTO IT
//   1. It patches a THIRD-PARTY PRIVATE method, which carries no compatibility
//      promise. An upstream rename makes the patch a no-op - which is the very
//      defect being fixed - so Install() ASSERTS its target resolved and says so
//      loudly, and the report tool reports the failure as a first-class state.
//   2. The companion's module initializer is LAZY (JAWABENCH_INIT_LINE_IS_LAZY_1):
//      it fires on the first jawa/ tool INVOCATION, not at assembly load. So the
//      very first jawa/ call of a session is bound BEFORE this patch exists and its
//      dropped keys are invisible. Every call after it is covered.
//   3. It sees ONLY what reaches BindArguments. Anything
//      ReflectedCapabilityBinding.NormalizeInvocationArguments discards or rewrites
//      upstream - kebab-case folding, legacy shapes - happened before this point.
//
// ⛔ NO jawa/ PREFIXES IN PROSE ANYWHERE IN THIS FILE'S DESCRIPTIONS. build.py scans
// the assembly for jawa/ literals and a docstring mention becomes a phantom tool.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using HarmonyLib;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    /// <summary>
    /// All Harmony contact is isolated in this one type on purpose. Nothing else in
    /// the assembly references HarmonyLib, so if 0Harmony were somehow absent the JIT
    /// only fails when Install() is actually called - inside a try/catch - rather than
    /// taking the whole companion's type load with it.
    /// </summary>
    internal static class JawaBenchArgGuard
    {
        internal const string TargetType = "RimBridgeServer.AnnotatedExtensionCapabilityProvider";
        internal const string TargetMethod = "BindArguments";

        private static readonly object Gate = new object();
        private static readonly List<DropRecord> Records = new List<DropRecord>();

        /// <summary>Bounded so a long session cannot grow this without limit.</summary>
        private const int MaxRecords = 400;

        internal sealed class DropRecord
        {
            public string method;
            public List<string> droppedParameters;
            public List<string> accepted;
            public int ticksGame;
            public int seq;
        }

        // ---- installation state, reported rather than assumed ---------------------
        internal static bool Installed;
        internal static string InstallError;      // null when Installed
        internal static bool Strict;              // opt-in: throw instead of recording
        internal static int Seen;                 // calls observed carrying unknown keys
        internal static int Bound;                // calls observed at all
        private static int _seq;

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
                        Log.Warning("[JawaBench] argument guard NOT installed: " + InstallError +
                                    " - unknown tool parameters stay silently dropped.");
                        return;
                    }
                    var m = AccessTools.Method(t, TargetMethod);
                    if (m == null)
                    {
                        InstallError = "method '" + TargetType + "." + TargetMethod +
                                       "' not found - upstream may have renamed or inlined it. " +
                                       "Methods present: " +
                                       string.Join(", ", t.GetMethods(AccessTools.all).Select(x => x.Name).Distinct().Take(40));
                        Log.Warning("[JawaBench] argument guard NOT installed: " + InstallError);
                        return;
                    }

                    var harmony = new Harmony("mandrake.jawabench.argguard");
                    harmony.Patch(m, prefix: new HarmonyMethod(
                        typeof(JawaBenchArgGuard).GetMethod(nameof(Prefix),
                            BindingFlags.Static | BindingFlags.NonPublic)));

                    Installed = true;
                    Log.Message("[JawaBench] argument guard installed on " + TargetType + "." + TargetMethod +
                                " - a tool argument matching no declared parameter is now RECORDED " +
                                "(not refused; strict mode is opt-in).");
                }
                catch (Exception e)
                {
                    InstallError = e.GetType().Name + ": " + e.Message;
                    Log.Warning("[JawaBench] argument guard NOT installed: " + InstallError);
                }
            }
        }

        /// <summary>
        /// 🔴 THIS PREFIX MUST NEVER CHANGE BEHAVIOUR AND MUST NEVER THROW, except the
        /// one deliberate throw under Strict. It returns void and declares no __result,
        /// so Harmony always runs the original. Everything else is inside a catch that
        /// swallows: a guard that breaks the binder would be far worse than the silent
        /// drop it exists to expose.
        /// </summary>
        private static void Prefix(MethodInfo method, IReadOnlyDictionary<string, object> arguments)
        {
            List<string> unknown = null;
            List<string> accepted = null;
            string name = null;
            try
            {
                if (method == null || arguments == null || arguments.Count == 0) return;

                var declared = new HashSet<string>(
                    method.GetParameters().Select(p => p.Name), StringComparer.OrdinalIgnoreCase);

                foreach (var k in arguments.Keys)
                {
                    if (declared.Contains(k)) continue;
                    if (unknown == null) unknown = new List<string>();
                    unknown.Add(k);
                }

                Interlocked.Increment(ref Bound);
                if (unknown == null) return;

                accepted = method.GetParameters().Select(p => p.Name).ToList();
                name = (method.DeclaringType != null ? method.DeclaringType.Name + "." : "") + method.Name;

                lock (Gate)
                {
                    Seen++;
                    _seq++;
                    Records.Add(new DropRecord
                    {
                        method = name,
                        droppedParameters = unknown,
                        accepted = accepted,
                        ticksGame = TicksSafe(),
                        seq = _seq
                    });
                    if (Records.Count > MaxRecords) Records.RemoveRange(0, Records.Count - MaxRecords);
                }

                Log.Warning("[JawaBench] " + name + " was given " + unknown.Count +
                            " argument(s) it does not declare and the bridge DROPPED them silently: " +
                            string.Join(", ", unknown.ToArray()) +
                            ". Accepted: " + string.Join(", ", accepted.ToArray()));
            }
            catch
            {
                // Swallowed on purpose - see the summary above. A guard that throws here
                // breaks every tool call on the bridge.
                return;
            }

            // The one deliberate throw, and only when a caller opted in. Outside the
            // catch above so a genuine strict refusal is not swallowed by it.
            if (Strict && unknown != null)
                throw new ArgumentException(
                    "Strict argument mode: " + name + " was given argument(s) it does not declare: " +
                    string.Join(", ", unknown.ToArray()) + ". Accepted: " +
                    string.Join(", ", (accepted ?? new List<string>()).ToArray()));
        }

        private static int TicksSafe()
        {
            try
            {
                return Current.Game != null && Find.TickManager != null ? Find.TickManager.TicksGame : -1;
            }
            catch { return -1; }
        }

        internal static List<DropRecord> Snapshot(int limit)
        {
            lock (Gate)
            {
                if (limit <= 0 || limit >= Records.Count) return new List<DropRecord>(Records);
                return Records.Skip(Records.Count - limit).ToList();
            }
        }

        internal static int Clear()
        {
            lock (Gate) { int n = Records.Count; Records.Clear(); return n; }
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/bridge_arg_report",
            Description =
                "Report every tool argument the BRIDGE SILENTLY DROPPED because it matched no " +
                "declared parameter - the defect that makes a typo'd argument name invisible " +
                "across every tool on the bridge, not just this companion's. Backed by a Harmony " +
                "prefix on the host's private argument binder, so it observes calls to ALL tools. " +
                "'report' is the default and lists what has been dropped this session; 'clear' " +
                "empties the record; 'strict' makes an unknown argument THROW from then on, and " +
                "'lenient' turns that back off. Strict is off by default on purpose: the binder " +
                "is shared, so refusing changes behaviour for every caller at once. " +
                "READ 'installed' FIRST - the patch target is a third-party private method and if " +
                "upstream renamed it this reports nothing while nothing is wrong with the call.",
            ResultDescription =
                "installed, installError, strict, callsObserved, callsWithDroppedArgs, and " +
                "records[] of method / droppedParameters / accepted / ticksGame. " +
                "installed=false means THIS INSTRUMENT IS BLIND, never that no arguments were dropped.")]
        public static async Task<object> BridgeArgReport(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'report' (default), 'clear', 'strict' or 'lenient'.")]
            string action = "report",
            [ToolParameter(Description = "Most recent N records to return. 0 or less returns all held (capped at 400).", DefaultValue = 50)]
            int limit = 50)
        {
            // 🔑 Deliberately NOT inside MainThread.InvokeAsync. Nothing here touches a
            // Map, a Pawn or any game object - it reads this assembly's own static
            // record behind its own lock. Hopping the main thread would make an
            // instrument for diagnosing a wedged bridge itself require an unwedged
            // main thread, which is precisely the failure it exists to diagnose.
            cancellationToken.ThrowIfCancellationRequested();

            var act = (action ?? "report").Trim().ToLowerInvariant();

            if (act == "clear")
            {
                int n = JawaBenchArgGuard.Clear();
                return await Task.FromResult<object>(new
                {
                    success = true,
                    action = "clear",
                    cleared = n,
                    installed = JawaBenchArgGuard.Installed,
                    installError = JawaBenchArgGuard.InstallError
                }).ConfigureAwait(false);
            }

            if (act == "strict" || act == "lenient")
            {
                if (!JawaBenchArgGuard.Installed)
                    return Fail("The guard is not installed, so strict mode would do nothing. " +
                                "This is a refusal, not a silent no-op.",
                        new { installError = JawaBenchArgGuard.InstallError, target = JawaBenchArgGuard.TargetType + "." + JawaBenchArgGuard.TargetMethod });

                bool before = JawaBenchArgGuard.Strict;
                JawaBenchArgGuard.Strict = (act == "strict");
                return await Task.FromResult<object>(new
                {
                    success = true,
                    action = act,
                    strictBefore = before,
                    strictAfter = JawaBenchArgGuard.Strict,
                    note = JawaBenchArgGuard.Strict
                        ? "Every tool on the bridge now THROWS on an argument it does not declare, this companion's and everyone else's. Turn it off with 'lenient'."
                        : "Unknown arguments are recorded again rather than refused."
                }).ConfigureAwait(false);
            }

            if (act != "report")
                return Fail("Unknown action '" + action + "'. Use 'report', 'clear', 'strict' or 'lenient'.");

            var recs = JawaBenchArgGuard.Snapshot(limit);
            return await Task.FromResult<object>(new
            {
                success = true,
                action = "report",
                installed = JawaBenchArgGuard.Installed,
                installError = JawaBenchArgGuard.InstallError,
                target = JawaBenchArgGuard.TargetType + "." + JawaBenchArgGuard.TargetMethod,
                strict = JawaBenchArgGuard.Strict,
                callsObserved = JawaBenchArgGuard.Bound,
                callsWithDroppedArgs = JawaBenchArgGuard.Seen,
                returned = recs.Count,
                records = recs.Select(r => new
                {
                    r.seq,
                    r.method,
                    r.droppedParameters,
                    r.accepted,
                    r.ticksGame
                }).ToList(),
                // ⚠️ Not decoration. installed=false and zero records are the SAME
                // reading here, and telling them apart is the whole point.
                blindWarning = JawaBenchArgGuard.Installed
                    ? null
                    : "NOT INSTALLED - this instrument is blind. Zero records means it never looked, not that nothing was dropped.",
                firstCallCaveat =
                    "The companion's module initializer is lazy, so the FIRST tool call of a session is bound before this patch exists. Its dropped arguments are invisible; every call after it is covered."
            }).ConfigureAwait(false);
        }
    }
}
