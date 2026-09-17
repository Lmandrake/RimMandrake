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
                // the most this can overshoot by. A limit hit INSIDE a type's method loop
                // (below) also breaks here via this same check, on the type boundary, so
                // `i` always names the first type NOT fully scanned - never a type left
                // half-walked.
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
                }

                // ⛔ No limit re-check here. Breaking at the BOTTOM of the body leaves `i` naming
                // the type just FULLY scanned, so resumeFromType would re-walk it and the caller
                // would get its matches twice (and scannedTypes would undercount by one). The
                // top-of-loop check above catches the same condition one iteration later with `i`
                // already advanced - which is the invariant this loop documents and relies on.
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

        // DEBUG_ACTION_ENUM_CRASH_1 - RimBridgeServer's OWN search_debug_actions and
        // list_debug_action_children(path="Actions") both NRE server-side on ANY query,
        // because RimWorldDebugActions.PrepareNode (and vanilla's own
        // LudeonTK.DebugTabMenu_Actions.InitActions underneath it) invoke every
        // [DebugActionYielder] EAGERLY and UNGUARDED while building the "Actions" root -
        // one broken yielder (Verse.DebugActionsIncidents.RitualSiegeWithSpecifics, which
        // NREs via Find.Storyteller/Find.CurrentMap when no game is loaded) poisons the
        // whole call. Confirmed by reading LudeonTK/DebugActionNode.cs and
        // DebugTabMenu_Actions.cs via RimSage: TrySetupChildren has no try/catch around
        // childGetter(), and InitActions has none around methodInfo.Invoke for a yielder.
        //
        // 🔴 Same constraint as jawa/debug_actions above: RimBridgeServer
        // (brrainz.rimbridgeserver, workshop 3727949765) ships assemblies only, no
        // Source/ - its PrepareNode cannot be edited by us, and patching vanilla's
        // InitActions/TrySetupChildren is explicitly out of scope (DEBUG_ACTION_ENUM_
        // CRASH_1's "not chasing"). The sanctioned fix is the same pattern already
        // shipped for search: a jawa/ replacement that does the invoking ITSELF, with a
        // try/catch around each individual yielder, so one broken node degrades to a
        // per-yielder error entry instead of taking down the whole response.
        //
        // This deliberately does NOT touch jawa/debug_actions' default behaviour above
        // (still never invokes a yielder unless asked) - this is the opt-in tool for a
        // caller who specifically needs yielder-produced actions (the "Actions" tree
        // content list_debug_action_children was trying to reach).
        [Tool(
            "jawa/debug_action_yielders",
            Description =
                "Safely invoke every [DebugActionYielder] method (the mod/vanilla-authored " +
                "enumerations that build dynamic debug-menu entries, e.g. incident-with-" +
                "specifics submenus) and return the action nodes they produce. Each yielder " +
                "runs inside its OWN try/catch, so one broken yielder (confirmed cause: " +
                "Verse.DebugActionsIncidents.RitualSiegeWithSpecifics NREing with no game " +
                "loaded) reports as a single failed entry, never a crashed whole-call - the " +
                "defect that makes the host's rimworld/search_debug_actions and " +
                "rimworld/list_debug_action_children(path=\"Actions\") both NRE on ANY query. " +
                "*** IT DOES INVOKE MOD/VANILLA CODE *** (unlike jawa/debug_actions), so treat " +
                "it as a probe with a real cost, not a free catalogue - a WALL-CLOCK BUDGET " +
                "still applies per yielder invocation is NOT individually bounded (a single " +
                "yielder that hangs will hang this call; only exceptions are contained).",
            ResultDescription =
                "success, matches[] of label / category / actionType / declaringType / method, " +
                "yieldersInvoked, yieldersFailed[] of {declaringType, method, error}, " +
                "scannedTypes, totalTypes, elapsedMs, truncated and resumeFromType.")]
        public static async Task<object> DebugActionYielders(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Case-insensitive substring, matched against the produced node's label/category " +
                "and the yielder's declaring type/method. Omit to return everything reached.")]
            string query = null,
            [ToolParameter(Description = "Stop after this many matches. 0 or less means no cap.", DefaultValue = 200)]
            int limit = 200,
            [ToolParameter(Description =
                "Wall-clock budget in milliseconds for the type-scan between yielder calls. " +
                "Does NOT bound an individual yielder invocation - only exceptions are caught, " +
                "not hangs. Clamped to 100..10000.", DefaultValue = 3000)]
            int maxMillis = 3000,
            [ToolParameter(Description =
                "Index into the type list to resume from, taken from a previous call's " +
                "resumeFromType.", DefaultValue = 0)]
            int resumeFromType = 0)
        {
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
            var yieldersFailed = new List<object>();
            int yieldersInvoked = 0;
            int typesFailed = 0;
            bool truncated = false;
            string stopReason = "completed";
            int i = resumeFromType;

            for (; i < total; i++)
            {
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
                    typesFailed++;
                    continue;
                }

                for (int m = 0; m < methods.Length; m++)
                {
                    var method = methods[m];
                    bool isYielder;
                    try { isYielder = method.GetCustomAttribute<DebugActionYielderAttribute>() != null; }
                    catch { continue; }
                    if (!isYielder) continue;

                    string declaring = types[i].FullName ?? types[i].Name;

                    // ⛔ THE FIX: this invocation is wrapped per-yielder. A broken yielder
                    // (RitualSiegeWithSpecifics being the confirmed live example) reports
                    // here and this loop simply moves to the next method - it is what
                    // InitActions/PrepareNode both fail to do.
                    IEnumerable<DebugActionNode> produced = null;
                    try
                    {
                        produced = (IEnumerable<DebugActionNode>)method.Invoke(null, null);
                        // Force materialization now, inside the same try - a yielder can
                        // defer its own exception into enumeration (yield return bodies do).
                        produced = produced?.ToList();
                    }
                    catch (Exception e)
                    {
                        var inner = e is TargetInvocationException tie && tie.InnerException != null ? tie.InnerException : e;
                        yieldersFailed.Add(new
                        {
                            declaringType = declaring,
                            method = method.Name,
                            error = inner.GetType().Name + ": " + inner.Message
                        });
                        continue;
                    }

                    yieldersInvoked++;
                    if (produced == null) continue;

                    foreach (var node in produced)
                    {
                        if (limit > 0 && matches.Count >= limit) break;
                        if (node == null) continue;

                        string label;
                        string category;
                        string actionType;
                        try { label = node.label; } catch { label = null; }
                        try { category = node.category; } catch { category = null; }
                        try { actionType = node.actionType.ToString(); } catch { actionType = null; }

                        if (q != null &&
                            (label == null || label.IndexOf(q, StringComparison.OrdinalIgnoreCase) < 0) &&
                            (category == null || category.IndexOf(q, StringComparison.OrdinalIgnoreCase) < 0) &&
                            declaring.IndexOf(q, StringComparison.OrdinalIgnoreCase) < 0 &&
                            method.Name.IndexOf(q, StringComparison.OrdinalIgnoreCase) < 0)
                            continue;

                        matches.Add(new
                        {
                            label,
                            category = category ?? "General",
                            actionType,
                            declaringType = declaring,
                            method = method.Name
                        });
                    }
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
                yieldersInvoked,
                yieldersFailed,
                yieldersFailedNote = yieldersFailed.Count > 0
                    ? "Each of these threw INSIDE its own try/catch and was skipped - it did not stop the scan. This is the fix for DEBUG_ACTION_ENUM_CRASH_1."
                    : null,
                scannedTypes = scanned,
                fromType = resumeFromType,
                totalTypes = total,
                typesFailed,
                elapsedMs = sw.ElapsedMilliseconds,
                budgetMs = maxMillis,
                truncated,
                stopReason,
                resumeFromType = truncated && i < total ? (int?)i : null,
                completenessWarning = truncated
                    ? "TRUNCATED (" + stopReason + "). matches[] is a FLOOR, not a complete list. Re-call with resumeFromType to continue."
                    : null,
                ticksGame = TicksGameSafe()
            }).ConfigureAwait(false);
        }
    }
}
