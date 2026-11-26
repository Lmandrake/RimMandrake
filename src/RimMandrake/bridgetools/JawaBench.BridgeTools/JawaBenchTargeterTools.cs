// jawa/targeter_pick: complete the targeter that a gizmo opened, on one cell, the way the player's click does.
//
// Why it exists (SHIP_TOW_LINE_1, 2026-11-26): a comp gizmo that calls Find.Targeter.BeginTargeting (the salvage winch's
// "Hook salvage") waits for a click that Targeter.ProcessInputEvents reads in OnGUI. rimworld/click_cell dispatches a
// click through selection, not through the targeter: the winch kept target=null (measured on ArchSmall). The GSS
// playtest reaches the targeter's private `action` by reflection for its own gizmos (JawaBenchGssPlaytest.GClick); this
// tool is that reach as a generic primitive, for any gizmo of any mod.
//
// Player fidelity: the candidates are the things at the cell (then the cell itself), filtered by the targeter's own
// TargetingParameters.CanTarget and its targetValidator, as the player's click under the mouse is. A refusal names
// which filter refused each candidate; nothing is invoked then.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
#if JAWA_GM_TOOLS
        private static readonly FieldInfo TgtAction = typeof(Targeter).GetField("action", BindingFlags.Instance | BindingFlags.NonPublic);
        private static readonly FieldInfo TgtParams = typeof(Targeter).GetField("targetParams", BindingFlags.Instance | BindingFlags.NonPublic);
        private static readonly FieldInfo TgtValidator = typeof(Targeter).GetField("targetValidator", BindingFlags.Instance | BindingFlags.NonPublic);

        [Tool(
            "jawa/targeter_pick",
            Description =
                "Complete the ACTIVE targeter (one a gizmo opened, e.g. after rimworld/execute_gizmo) on the cell x,z, as " +
                "the player's click does: the things at the cell, then the cell itself, filtered by the targeter's own " +
                "TargetingParameters.CanTarget and targetValidator; `thing` (a ThingID) picks one of them. The first that " +
                "passes is given to the targeter's callback and targeting stops. REFUSES, invoking nothing: no targeter " +
                "active, a targeter driven by a verb or ability (no plain callback), a cell off the map, or no candidate " +
                "passing (refused[] names each candidate and the filter). rimworld/click_cell does NOT reach a targeter. " +
                "Read the effect afterwards from the game (the callback's own result is not observable here). GM-gated.",
            ResultDescription = "success, picked (thing id or cell), candidates, refused[] {target, why}, stillTargeting, ticksGame.")]
        public static async Task<object> TargeterPick(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Cell x.")] int x,
            [ToolParameter(Description = "Cell z.")] int z,
            [ToolParameter(Description = "Optional ThingID at that cell to pick; blank = the first candidate that passes.")] string thing = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                Targeter tg = Find.Targeter;
                if (tg == null || !tg.IsTargeting) return Fail("No targeter is active: press the gizmo first (rimworld/execute_gizmo).");
                var act = TgtAction?.GetValue(tg) as Action<LocalTargetInfo>;
                var parms = TgtParams?.GetValue(tg) as TargetingParameters;
                var valid = TgtValidator?.GetValue(tg) as Func<LocalTargetInfo, bool>;
                if (act == null || parms == null)
                    return Fail("The active targeter has no plain callback (a verb or ability targeter); this tool does not drive it.",
                        new { hasAction = act != null, hasParams = parms != null });
                var cell = new IntVec3(x, 0, z);
                if (!cell.InBounds(map)) return Fail("Cell " + x + "," + z + " is off the map.");

                var cands = new List<LocalTargetInfo>();
                foreach (Thing t in cell.GetThingList(map).ToList())
                    if (string.IsNullOrEmpty(thing) || t.ThingID == thing || "Thing_" + t.ThingID == thing) cands.Add(new LocalTargetInfo(t));
                if (string.IsNullOrEmpty(thing)) cands.Add(new LocalTargetInfo(cell));
                if (cands.Count == 0)
                    return Fail("No thing " + thing + " at " + x + "," + z + ".",
                        new { thingsAtCell = cell.GetThingList(map).Select(t => t.ThingID).ToList() });

                var refused = new List<object>();
                foreach (LocalTargetInfo c in cands)
                {
                    string label = c.HasThing ? c.Thing.ThingID : "cell " + x + "," + z;
                    TargetInfo ti = c.HasThing ? new TargetInfo(c.Thing) : new TargetInfo(cell, map);
                    if (!parms.CanTarget(ti)) { refused.Add(new { target = label, why = "TargetingParameters.CanTarget refused" }); continue; }
                    if (valid != null && !valid(c)) { refused.Add(new { target = label, why = "the targeter's targetValidator refused" }); continue; }
                    tg.StopTargeting();
                    act(c);
                    return (object)new
                    {
                        success = true,
                        picked = label,
                        candidates = cands.Count,
                        refused,
                        stillTargeting = Find.Targeter.IsTargeting,
                        ticksGame = TicksGameSafe(),
                    };
                }
                return Fail("No candidate at " + x + "," + z + " passes the targeter's filters; nothing was invoked.",
                    new { candidates = cands.Count, refused, stillTargeting = tg.IsTargeting });
            }, cancellationToken);
        }
#endif
    }
}
