// JawaBenchDebugActionTools.cs - enumerate the dev-menu surface WITHOUT wedging the bridge.
//
// DEBUG_ACTION_SEARCH_WEDGES_BRIDGE_1, option 2 - "a jawa/ replacement that bounds the
// work", which the item names as the only real fix available to us.
//
// 🔴 WHY THE HOST'S TOOL CANNOT BE FIXED. rimworld/search_debug_actions belongs to
// RimBridgeServer (brrainz.rimbridgeserver, workshop 3727949765), which ships assemblies
// only - no Source/. So we cannot filter during its walk and cannot add a refusal
// threshold. Measured 2026-08-26 by CHECK, live, 582 active mods, one map, tick 1174:
//     rimworld/search_debug_actions {"query": "generate map", "limit": 10}
//       -> RimBridgeError: timed out after 30.0s
//       -> every subsequent call timed out for MINUTES; the process stayed alive at ~7 GB
// One call cost several minutes of bridge time and ended a line of work.
//
// 🔑 WHERE THE COST ACTUALLY IS, READ OUT OF 1.6 SOURCE (LudeonTK/DebugTabMenu_Actions.cs
// InitActions). Two separate costs, and only one of them is obvious:
//   1. It walks GenTypes.AllTypes and calls GetMethods(Static|Public|NonPublic) on every
//      one. On 582 mods that is tens of thousands of types.
//   2. ⛔ THE EXPENSIVE ONE: for every method carrying [DebugActionYielder] it CALLS IT -
//      `methodInfo.Invoke(null, null)` - and enumerates the result. A yielder is arbitrary
//      mod code that commonly walks a whole DefDatabase to build its list. So "listing the
//      menu" secretly RUNS several hundred mod-authored enumerations on the main thread.
// ⇒ A `limit` applied to the RESULT cannot bound either cost. That is the defect, exactly.
//
// WHAT THIS TOOL DOES INSTEAD
//   * Filters on the query DURING the walk, so the query bounds the WORK.
//   * ⛔ NEVER invokes a yielder. It reports how many it SKIPPED, so the omission is a
//     stated number rather than a silent gap - the surface here is [DebugAction] methods,
//     which is most of the menu but provably not all of it.
//   * Carries a WALL-CLOCK BUDGET and stops when it expires, returning `truncated` and a
//     `resumeFromType` index. A tool that cannot exceed its budget cannot wedge the bridge,
//     which is the whole reason this exists.
//   * Executes nothing. It is a catalogue, not a trigger.
//
// ⚠️ Per-type try/catch is not defensive noise: GetMethods throws on a type whose
// dependencies failed to load, which in a 582-mod stack is normal, and one such type
// would otherwise abort the entire walk.
//
// THREAD AFFINITY: the walk touches no Map, Pawn or Thing - only reflection over loaded
// types and the ProgramState/ModsConfig statics that DebugActionAttribute itself reads.
// It deliberately does NOT hop the main thread; see the note on the tool.

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using LudeonTK;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/debug_actions",
            Description =
                "List the game's dev-menu debug actions with the query applied DURING the walk " +
                "and a WALL-CLOCK BUDGET, so the search cannot wedge the bridge. The host's own " +
                "search enumerates the entire menu and filters afterwards - on 582 mods that " +
                "timed out at 30s and blocked every other caller for minutes, because a limit on " +
                "the RESULT does not limit the WORK. This one stops when its budget expires and " +
                "says so, returning resumeFromType to continue. " +
                "*** IT EXECUTES NOTHING *** - it is a catalogue, not a trigger. " +
                "⛔ It also never invokes a [DebugActionYielder], which is where the real cost " +
                "lives: the vanilla menu builder CALLS every yielder, running hundreds of " +
                "mod-authored enumerations on the main thread. Yielders are counted and reported " +
                "as skipped, so what is missing is a number rather than a silent gap.",
            ResultDescription =
                "success, matches[] of name / category / declaringType / method / actionType / " +
                "allowedGameStates / allowedNow / requiresDlc, plus scannedTypes, totalTypes, " +
                "yieldersSkipped, elapsedMs, truncated and resumeFromType. " +
                "truncated=true means the answer is a FLOOR, not a complete list.")]
        public static async Task<object> DebugActions(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Case-insensitive substring, matched against the action name, its category and " +
                "its declaring type. Omit to list everything the budget reaches - on a large mod " +
                "list that will truncate, which is the point.")]
            string query = null,
            [ToolParameter(Description = "Stop after this many matches. 0 or less means no cap.", DefaultValue = 100)]
            int limit = 100,
            [ToolParameter(Description =
                "Wall-clock budget in milliseconds. The walk stops here even mid-scan and reports " +
                "truncated=true. Clamped to 100..10000 - a budget large enough to wedge the bridge " +
                "is not offered.", DefaultValue = 2000)]
            int maxMillis = 2000,
            [ToolParameter(Description =
                "Index into the type list to resume from, taken from a previous call's " +
                "resumeFromType. Lets a big sweep be paid for in bounded instalments.", DefaultValue = 0)]
            int resumeFromType = 0,
            [ToolParameter(Description =
                "Only actions whose IsAllowedInCurrentGameState is true right now (the dev menu's " +
                "own gate: ProgramState, world-vs-map, and DLC).", DefaultValue = false)]
            bool allowedNowOnly = false)
        {
            // 🔑 Deliberately NOT inside MainThread.InvokeAsync, and that is the design.
            // This touches no game object - only reflection over loaded types plus the same
            // ProgramState/ModsConfig statics DebugActionAttribute reads. Hopping the main
            // thread would put this walk on the exact thread it exists to keep free, which
            // is what makes the host's version a wedge rather than merely a slow call.
            cancellationToken.ThrowIfCancellationRequested();

            if (maxMillis < 100) maxMillis = 100;
            if (maxMillis > 10000) maxMillis = 10000;

            var q = string.IsNullOrWhiteSpace(query) ? null : query.Trim();
            var sw = Stopwatch.StartNew();

            List<Type> types;
            try { types = GenTypes.AllTypes.ToList(); }
            catch (Exception e) { return Fail("Could not enumerate loaded types: " + e.GetType().Name + ": " + e.Message); }

            int total = types.Count;
            if (resumeFromType < 0) resumeFromType = 0;
            if (resumeFromType >= total)
                return Fail("resumeFromType " + resumeFromType + " is past the end of the type list (" + total + ").");

            var matches = new List<object>();
            int i = resumeFromType;
            int yieldersSkipped = 0;
            int typesFailed = 0;
            bool truncated = false;
            string stopReason = "completed";

            for (; i < total; i++)
            {
                // Budget and cap are checked BEFORE each type, so the cost of one type is
                // the most this can overshoot by.
                if (sw.ElapsedMilliseconds >= maxMillis) { truncated = true; stopReason = "budget"; break; }
                if (limit > 0 && matches.Count >= limit) { truncated = true; stopReason = "limit"; break; }
                if (cancellationToken.IsCancellationRequested) { truncated = true; stopReason = "cancelled"; break; }

                MethodInfo[] methods;
                try
                {
                    methods = types[i].GetMethods(BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic);
                }
                catch
                {
                    // Normal in a large stack: a type whose dependencies failed to load.
                    // Counted, not swallowed - an unexplained hole in a census is worse
                    // than a small one that is reported.
                    typesFailed++;
                    continue;
                }

                for (int m = 0; m < methods.Length; m++)
                {
                    var method = methods[m];

                    DebugActionAttribute attr = null;
                    try { attr = method.GetCustomAttribute<DebugActionAttribute>(); }
                    catch { continue; }

                    if (attr == null)
                    {
                        // ⛔ Counted and NOT invoked. This is the whole cost saving, and it
                        // is also the whole blind spot, so it is reported either way.
                        try
                        {
                            if (method.GetCustomAttribute<DebugActionYielderAttribute>() != null) yieldersSkipped++;
                        }
                        catch { }
                        continue;
                    }

                    string name;
                    try { name = string.IsNullOrEmpty(attr.name) ? GenText.SplitCamelCase(method.Name) : attr.name; }
                    catch { name = method.Name; }
                    string category = attr.category ?? "General";
                    string declaring = types[i].FullName ?? types[i].Name;

                    // ---- the filter, applied DURING the walk -----------------------
                    if (q != null &&
                        name.IndexOf(q, StringComparison.OrdinalIgnoreCase) < 0 &&
                        category.IndexOf(q, StringComparison.OrdinalIgnoreCase) < 0 &&
                        declaring.IndexOf(q, StringComparison.OrdinalIgnoreCase) < 0)
                        continue;

                    bool allowedNow;
                    try { allowedNow = attr.IsAllowedInCurrentGameState; }
                    catch { allowedNow = false; }
                    if (allowedNowOnly && !allowedNow) continue;

                    var dlc = new List<string>();
                    if (attr.requiresRoyalty) dlc.Add("Royalty");
                    if (attr.requiresIdeology) dlc.Add("Ideology");
                    if (attr.requiresBiotech) dlc.Add("Biotech");
                    if (attr.requiresAnomaly) dlc.Add("Anomaly");
                    if (attr.requiresOdyssey) dlc.Add("Odyssey");

                    matches.Add(new
                    {
                        name,
                        category,
                        declaringType = declaring,
                        method = method.Name,
                        actionType = attr.actionType.ToString(),
                        allowedGameStates = attr.allowedGameStates.ToString(),
                        allowedNow,
                        requiresDlc = dlc,
                        hideInSubMenu = attr.hideInSubMenu
                    });

                    if (limit > 0 && matches.Count >= limit) { truncated = true; stopReason = "limit"; break; }
                }
            }

            sw.Stop();
            int scanned = i - resumeFromType;

            return await Task.FromResult<object>(new
            {
                success = true,
                query = q,
                matched = matches.Count,
                matches,
                scannedTypes = scanned,
                fromType = resumeFromType,
                totalTypes = total,
                typesFailed,
                // ⛔ The stated blind spot. The vanilla menu INVOKES these to build its
                // list; this tool never does, so any action a yielder would have produced
                // is absent from the answer above.
                yieldersSkipped,
                yieldersNote =
                    "Yielder methods were counted and NEVER invoked - invoking them is what makes the vanilla walk expensive. Any action a yielder would have produced is NOT in matches[].",
                elapsedMs = sw.ElapsedMilliseconds,
                budgetMs = maxMillis,
                truncated,
                stopReason,
                // Only meaningful when truncated; null otherwise so a caller cannot loop forever.
                resumeFromType = truncated && i < total ? (int?)i : null,
                // ⚠️ Not decoration. A truncated answer that reads as complete is how a
                // census lies, and this one truncates BY DESIGN on a large mod list.
                completenessWarning = truncated
                    ? "TRUNCATED (" + stopReason + "). matches[] is a FLOOR, not a complete list. Re-call with resumeFromType to continue."
                    : null,
                ticksGame = TicksGameSafe()
            }).ConfigureAwait(false);
        }
    }
}
