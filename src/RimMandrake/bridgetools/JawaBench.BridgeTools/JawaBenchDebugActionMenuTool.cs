// JawaBenchDebugActionMenuTool.cs - run a debug action AND read / pick the FloatMenu it opens, in ONE main-thread call.
//
// BRIDGE_FLOATMENU_FIX_DEBUG_PICKER_UNREADABLE. Measured live (BENCH 2026-10-23, FOUNDRY 2026-10-29, min list):
//     rimworld/execute_debug_action {path:"Actions\\Tanks: fill ALL on map to max (pick liquid)"}
//       -> success, effects.openedWindowTypes=[Verse.FloatMenu]
//     the very next call (rimworld/get_context_menu_options, jawa/window_list_close list) -> no FloatMenu at all.
// The menu opens and is gone before any later call can read it, so nothing could be picked and the tanks stayed 0/26.
// The gizmo route opens the IDENTICAL menu (FlowWorksTankDebug.PickLiquid) and stays readable, so the menu is fine and
// what kills it is the host's execute path (likely FloatMenu.vanishIfMouseDistant with no real mouse near it). Both
// host tools ship without source (RimBridgeServer), so the fix cannot go there.
//
// ✅ THE ROUTE AROUND IT: never let a frame pass between "the menu opened" and "the menu was read". This tool resolves
// the [DebugAction] method itself, invokes it on the main thread, and in that same main-thread slice reads every
// FloatMenu the action added (labels, disabled flags) and, when asked, runs the picked option's own action. No frame,
// no mouse, no vanish. A menu left open is also pinned (vanishIfMouseDistant=false) so a later call can still read it.
//
// It also picks from a FloatMenu ALREADY open (path omitted): the newest one on the WindowStack.
//
// Scope, stated: only DebugActionType.Action methods with no parameters (the dev menu's plain buttons). A ToolMap /
// ToolMapForPawns action needs a map click and is refused by name; [DebugActionYielder] children are not reachable.

using System;
using System.Collections.Concurrent;
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
        private static readonly FieldInfo DamFloatMenuOptions =
            typeof(FloatMenu).GetField("options", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);
        private static readonly FieldInfo DamVanishField =
            typeof(FloatMenu).GetField("vanishIfMouseDistant", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);

        // name|category -> resolved methods; a debug action's identity does not change within a process.
        private static readonly ConcurrentDictionary<string, List<MethodInfo>> DamCache = new ConcurrentDictionary<string, List<MethodInfo>>();

        /// <summary>"Actions\\RMFlowWorks\\Tanks: fill ALL..." -> leaf name + the path's other segments (category candidates).</summary>
        internal static void DamSplitPath(string path, out string leaf, out List<string> segments)
        {
            var parts = (path ?? "").Replace('/', '\\').Split(new[] { '\\' }, StringSplitOptions.RemoveEmptyEntries)
                .Select(s => s.Trim()).Where(s => s.Length > 0).ToList();
            leaf = parts.Count == 0 ? "" : parts[parts.Count - 1];
            segments = parts.Take(Math.Max(0, parts.Count - 1)).ToList();
        }

        /// <summary>The option to pick: exact label (case-insensitive), else the ONE label containing the text.
        /// -1 with a reason when absent or ambiguous. pickIndex >= 0 wins over text.</summary>
        internal static int DamChoose(IList<string> labels, string pick, int pickIndex, out string why)
        {
            why = null;
            if (pickIndex >= 0)
            {
                if (pickIndex < labels.Count) return pickIndex;
                why = "pickIndex " + pickIndex + " is past the last option (" + labels.Count + ").";
                return -1;
            }
            string p = (pick ?? "").Trim();
            if (p.Length == 0) { why = "nothing to pick"; return -1; }
            var exact = Enumerable.Range(0, labels.Count).Where(i => string.Equals((labels[i] ?? "").Trim(), p, StringComparison.OrdinalIgnoreCase)).ToList();
            if (exact.Count >= 1) return exact[0];
            var part = Enumerable.Range(0, labels.Count).Where(i => (labels[i] ?? "").IndexOf(p, StringComparison.OrdinalIgnoreCase) >= 0).ToList();
            if (part.Count == 1) return part[0];
            why = part.Count == 0 ? "no option label contains '" + p + "'." : "'" + p + "' matches " + part.Count + " options; give the exact label or pickIndex.";
            return -1;
        }

        private static string DamName(MethodInfo m, DebugActionAttribute a)
        {
            try { return string.IsNullOrEmpty(a.name) ? GenText.SplitCamelCase(m.Name) : a.name; }
            catch { return m.Name; }
        }

        /// <summary>Every [DebugAction] method named 'leaf' (budgeted walk, off the main thread, cached).</summary>
        private static List<MethodInfo> DamResolve(string leaf, string declaringType, int maxMillis, out bool truncated)
        {
            truncated = false;
            string key = leaf + "|" + (declaringType ?? "");
            if (DamCache.TryGetValue(key, out var hit)) return hit;
            var found = new List<MethodInfo>();
            IEnumerable<Type> types;
            if (!string.IsNullOrEmpty(declaringType))
            {
                Type t = GenTypes.GetTypeInAnyAssembly(declaringType);
                types = t == null ? Enumerable.Empty<Type>() : new[] { t };
            }
            else types = GenTypes.AllTypes;
            var sw = Stopwatch.StartNew();
            foreach (Type t in types)
            {
                if (sw.ElapsedMilliseconds >= maxMillis) { truncated = true; break; }
                MethodInfo[] ms;
                try { ms = t.GetMethods(BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly); }
                catch { continue; }
                foreach (MethodInfo m in ms)
                {
                    DebugActionAttribute a;
                    try { a = m.GetCustomAttribute<DebugActionAttribute>(); } catch { continue; }
                    if (a != null && string.Equals(DamName(m, a), leaf, StringComparison.OrdinalIgnoreCase)) found.Add(m);
                }
            }
            if (!truncated && found.Count > 0) DamCache[key] = found;
            return found;
        }

        // FloatMenu's title field has been public and private across versions; read it by name, never compile against it
        private static readonly FieldInfo DamTitleField =
            typeof(FloatMenu).GetField("title", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);

        [Tool(
            "jawa/debug_action_menu",
            Description =
                "Run a dev-menu debug action and READ (optionally PICK) the FloatMenu it opens, all in ONE main-thread " +
                "call. Built because rimworld/execute_debug_action's picker menus vanish before the next call can read " +
                "them (BRIDGE_FLOATMENU_FIX_DEBUG_PICKER_UNREADABLE: 'Tanks: fill ALL on map to max (pick liquid)' " +
                "opened a FloatMenu that get_context_menu_options never saw). path = the action's name, optionally " +
                "prefixed by segments such as 'Actions\\RMFlowWorks\\' (a segment equal to the action's category " +
                "narrows an ambiguous name). pick = an option label (exact, else a unique substring) or pickIndex; the " +
                "picked option's own action runs and the menu closes. With no pick the options are returned and the " +
                "menu is left open and pinned (vanishIfMouseDistant off), so a later call with path omitted can pick " +
                "from it. path omitted = act on the newest FloatMenu already open. Only DebugActionType.Action " +
                "methods with no parameters; map-click tools are refused by name. Executes the action: GM-gated.",
            ResultDescription =
                "success, action {name, category, declaringType, method}, menus[] of {title, options[] of {index, " +
                "label, disabled}}, picked {index, label} or null, menuOpenAfter, ticksGame.")]
        public static async Task<object> DebugActionMenu(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "The debug action's name, optionally path-prefixed ('Actions\\Tanks: fill ALL on map to max (pick liquid)'). Omit to act on the newest open FloatMenu.")]
            string path = null,
            [ToolParameter(Description = "Option label to pick: exact (case-insensitive), else the one label containing it.")]
            string pick = null,
            [ToolParameter(Description = "Option index to pick (0-based); wins over pick. -1 = none.", DefaultValue = -1)]
            int pickIndex = -1,
            [ToolParameter(Description = "Type.FullName declaring the action; skips the type walk when given.")]
            string declaringType = null,
            [ToolParameter(Description = "Wall-clock budget for the type walk, ms (100..10000).", DefaultValue = 5000)]
            int maxMillis = 5000)
        {
            cancellationToken.ThrowIfCancellationRequested();
            if (maxMillis < 100) maxMillis = 100;
            if (maxMillis > 10000) maxMillis = 10000;
            bool wantPick = pickIndex >= 0 || !string.IsNullOrWhiteSpace(pick);

            MethodInfo method = null;
            DebugActionAttribute attr = null;
            if (!string.IsNullOrWhiteSpace(path))
            {
                DamSplitPath(path, out string leaf, out List<string> segs);
                // Off the main thread on purpose, as jawa/debug_actions: reflection only, and the walk must not hold
                // the thread the game draws on.
                List<MethodInfo> found;
                bool truncated;
                try { found = DamResolve(leaf, declaringType, maxMillis, out truncated); }
                catch (Exception e) { return Fail("Resolving '" + leaf + "' threw " + e.GetType().Name + ": " + e.Message); }
                if (found.Count > 1 && segs.Count > 0)
                {
                    var narrowed = found.Where(m => segs.Any(s => string.Equals(m.GetCustomAttribute<DebugActionAttribute>()?.category, s, StringComparison.OrdinalIgnoreCase))).ToList();
                    if (narrowed.Count > 0) found = narrowed;
                }
                if (found.Count == 0)
                    return Fail("No [DebugAction] named '" + leaf + "'" + (truncated ? " within the " + maxMillis + " ms walk budget (raise maxMillis or pass declaringType)." : "."),
                        new { truncated });
                if (found.Count > 1)
                    return Fail("'" + leaf + "' names " + found.Count + " debug actions; prefix the path with the category or pass declaringType.",
                        new { candidates = found.Select(m => new { declaringType = m.DeclaringType?.FullName, method = m.Name, category = m.GetCustomAttribute<DebugActionAttribute>()?.category }).ToList() });
                method = found[0];
                attr = method.GetCustomAttribute<DebugActionAttribute>();
                if (attr.actionType != DebugActionType.Action || method.GetParameters().Length != 0)
                    return Fail("'" + leaf + "' is a " + attr.actionType + " action with " + method.GetParameters().Length +
                        " parameter(s); this tool runs only plain DebugActionType.Action buttons (a map-click tool needs rimworld/execute_debug_action with a cell).");
            }
            else if (!wantPick)
                return Fail("Give path (run a debug action) or pick/pickIndex (choose on the newest open FloatMenu).");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var actionInfo = method == null ? null : new
                {
                    name = DamName(method, attr),
                    category = attr.category ?? "General",
                    declaringType = method.DeclaringType?.FullName,
                    method = method.Name
                };
                List<FloatMenu> menus;
                if (method != null)
                {
                    bool allowed;
                    try { allowed = attr.IsAllowedInCurrentGameState; } catch { allowed = false; }
                    if (!allowed)
                        return Fail("'" + actionInfo.name + "' is not allowed in the current game state (" + attr.allowedGameStates + ").", new { action = actionInfo });
                    var before = new HashSet<Window>(Find.WindowStack.Windows);
                    try { method.Invoke(null, null); }
                    catch (Exception e)
                    {
                        Exception inner = e.InnerException ?? e;
                        return Fail("The debug action threw " + inner.GetType().Name + ": " + inner.Message, new { action = actionInfo });
                    }
                    menus = Find.WindowStack.Windows.OfType<FloatMenu>().Where(w => !before.Contains(w)).ToList();
                }
                else
                {
                    FloatMenu newest = Find.WindowStack.Windows.OfType<FloatMenu>().LastOrDefault();
                    menus = newest == null ? new List<FloatMenu>() : new List<FloatMenu> { newest };
                }

                var menuRows = menus.Select(fm =>
                {
                    var opts = (DamFloatMenuOptions?.GetValue(fm) as List<FloatMenuOption>) ?? new List<FloatMenuOption>();
                    return new
                    {
                        title = DamTitleField?.GetValue(fm) as string,
                        options = opts.Select((o, i) => new { index = i, label = o?.Label ?? "", disabled = o?.Disabled ?? true }).ToList()
                    };
                }).ToList();

                object picked = null;
                string pickRefusal = null;
                FloatMenu target = menus.LastOrDefault();
                if (wantPick)
                {
                    if (target == null) pickRefusal = method == null ? "No FloatMenu is open." : "The action opened no FloatMenu.";
                    else
                    {
                        var opts = (DamFloatMenuOptions?.GetValue(target) as List<FloatMenuOption>) ?? new List<FloatMenuOption>();
                        int idx = DamChoose(opts.Select(o => o?.Label ?? "").ToList(), pick, pickIndex, out string why);
                        if (idx < 0) pickRefusal = why;
                        else if (opts[idx].Disabled) pickRefusal = "Option " + idx + " '" + opts[idx].Label + "' is disabled.";
                        else if (opts[idx].action == null) pickRefusal = "Option " + idx + " '" + opts[idx].Label + "' has no action.";
                        else
                        {
                            FloatMenuOption chosen = opts[idx];
                            // close first, as a real click does, so an action that opens a follow-up menu is not closed with it
                            Find.WindowStack.TryRemove(target, false);
                            try { chosen.action(); }
                            catch (Exception e)
                            {
                                Exception inner = e.InnerException ?? e;
                                return Fail("Option '" + chosen.Label + "' threw " + inner.GetType().Name + ": " + inner.Message,
                                    new { action = actionInfo, menus = menuRows });
                            }
                            picked = new { index = idx, label = chosen.Label };
                        }
                    }
                }
                // a menu left standing is pinned so the next bridge call can still see it
                bool pinned = false;
                foreach (FloatMenu fm in Find.WindowStack.Windows.OfType<FloatMenu>())
                    if (DamVanishField != null) { DamVanishField.SetValue(fm, false); pinned = true; }
                if (pickRefusal != null)
                    return Fail("Not picked: " + pickRefusal, new { action = actionInfo, menus = menuRows });
                return (object)new
                {
                    success = true,
                    action = actionInfo,
                    menus = menuRows,
                    picked,
                    menuOpenAfter = Find.WindowStack.Windows.OfType<FloatMenu>().Count(),
                    pinned,
                    ticksGame = Find.TickManager?.TicksGame ?? -1
                };
            });
        }
    }
}
